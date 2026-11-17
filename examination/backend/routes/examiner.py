
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, request, session
from sqlalchemy import or_

from models import (
    db,
    User,
    Examination,
    ExaminationSlot,
    ExamAssignment,
    Booking,
    Rubric,
    Evaluation,
    EvaluationMark
)
from routes.auth import role_required


examiner_bp = Blueprint("examiner", __name__)

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# HELPERS
# ==========================================

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_datetime(value):
    """
    ISO 8601 datetime input.
    Without a timezone, assume India time.
    Store as naive UTC, consistent with Step 5.
    """
    if not isinstance(value, str):
        raise ValueError("Datetime must be a string")

    parsed = datetime.fromisoformat(
        value.strip().replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=IST)

    return parsed.astimezone(
        timezone.utc
    ).replace(tzinfo=None)


def to_ist_string(value):
    if value is None:
        return None

    return (
        value.replace(tzinfo=timezone.utc)
        .astimezone(IST)
        .isoformat()
    )


def current_examiner():
    user_id = session.get("user_id")
    return db.session.get(User, user_id)


def slot_to_dict(slot):
    return {
        "id": slot.id,
        "examination_id": slot.examination_id,
        "examiner_id": slot.examiner_id,
        "start_time": to_ist_string(slot.start_time),
        "end_time": to_ist_string(slot.end_time),
        "capacity": slot.capacity,
        "status": slot.status,
        "meeting_link": slot.meeting_link,
        "booked_count": Booking.query.filter_by(
            slot_id=slot.id
        ).filter(
            Booking.status != "cancelled"
        ).count()
    }


def assigned_examination(exam_id, examiner_id):
    exam = db.session.get(Examination, exam_id)

    if not exam:
        return None

    assignment = ExamAssignment.query.filter_by(
        examination_id=exam_id,
        examiner_id=examiner_id
    ).first()

    if not assignment:
        return None

    return exam


def slot_creation_error(exam):
    now = utc_now()

    if exam.status != "Slot Creation":
        return (
            "Examination must be in "
            "'Slot Creation' status"
        )

    if not (
        exam.slot_creation_start
        <= now
        <= exam.slot_creation_end
    ):
        return "Outside slot creation period"

    if now >= exam.booking_start:
        return (
            "Cannot modify slots after "
            "student booking begins"
        )

    return None


def slot_has_bookings(slot_id):
    # Even cancelled bookings are retained as
    # historical records, so block modifications.
    return Booking.query.filter_by(
        slot_id=slot_id
    ).first() is not None


def overlapping_slot(
    examiner_id, start_time, end_time, exclude_id=None
):
    query = ExaminationSlot.query.filter(
        ExaminationSlot.examiner_id == examiner_id,
        ExaminationSlot.start_time < end_time,
        ExaminationSlot.end_time > start_time
    )

    if exclude_id is not None:
        query = query.filter(
            ExaminationSlot.id != exclude_id
        )

    return query.first()


def validate_slot_data(data, exam, examiner_id, existing=None):
    if not isinstance(data, dict):
        return None, "Valid JSON data is required"

    fields = {}

    for key in ("start_time", "end_time"):
        value = data.get(
            key,
            getattr(existing, key) if existing else None
        )

        if value is None:
            return None, f"{key} is required"

        if isinstance(value, datetime):
            fields[key] = value
        else:
            try:
                fields[key] = to_utc_datetime(value)
            except (ValueError, TypeError, OverflowError):
                return None, f"Invalid {key}"

    start_time = fields["start_time"]
    end_time = fields["end_time"]

    if start_time >= end_time:
        return None, "End time must be after start time"

    if start_time <= utc_now():
        return None, "Slot must be scheduled in the future"

    if start_time < exam.booking_end:
        return None, (
            "Slot must start after "
            "student booking closes"
        )

    duration_minutes = (
        end_time - start_time
    ).total_seconds() / 60

    if abs(duration_minutes - exam.duration) > 0.000001:
        return None, (
            f"Slot duration must be "
            f"{exam.duration} minutes"
        )

    capacity = data.get(
        "capacity",
        existing.capacity if existing else None
    )

    try:
        if isinstance(capacity, bool):
            raise ValueError()

        capacity_number = int(capacity)

        if str(capacity).strip() != str(capacity_number):
            raise ValueError()

        if capacity_number <= 0:
            raise ValueError()

    except (TypeError, ValueError):
        return None, "Capacity must be a positive integer"

    fields["capacity"] = capacity_number

    meeting_link = data.get(
        "meeting_link",
        existing.meeting_link if existing else None
    )

    if meeting_link is not None:
        if not isinstance(meeting_link, str):
            return None, "Meeting link must be text"

        meeting_link = meeting_link.strip()

        if len(meeting_link) > 500:
            return None, "Meeting link is too long"

    fields["meeting_link"] = meeting_link

    status = data.get(
        "status",
        existing.status if existing else "active"
    )

    if status not in ("active", "inactive"):
        return None, (
            "Slot status must be active or inactive"
        )

    fields["status"] = status

    conflict = overlapping_slot(
        examiner_id,
        start_time,
        end_time,
        existing.id if existing else None
    )

    if conflict:
        return None, (
            f"Slot overlaps with existing "
            f"slot ID {conflict.id}"
        )

    return fields, None


def get_owned_slot(slot_id, examiner_id):
    return ExaminationSlot.query.filter_by(
        id=slot_id,
        examiner_id=examiner_id
    ).first()


# ==========================================
# EXAMINER DASHBOARD
# ==========================================

@examiner_bp.route("/dashboard", methods=["GET"])
@role_required("examiner")
def examiner_dashboard():
    examiner = current_examiner()

    assignments = ExamAssignment.query.filter_by(
        examiner_id=examiner.id
    ).count()

    slots = ExaminationSlot.query.filter_by(
        examiner_id=examiner.id
    ).count()

    return jsonify({
        "message": "Examiner dashboard",
        "examiner": {
            "id": examiner.id,
            "name": examiner.name,
            "email": examiner.email
        },
        "assigned_examinations": assignments,
        "created_slots": slots
    }), 200


# ==========================================
# VIEW ASSIGNED EXAMINATIONS
# ==========================================

@examiner_bp.route(
    "/examinations",
    methods=["GET"]
)
@role_required("examiner")
def get_assigned_examinations():
    examiner = current_examiner()

    assignments = ExamAssignment.query.filter_by(
        examiner_id=examiner.id
    ).all()

    results = []

    for assignment in assignments:
        exam = db.session.get(
            Examination,
            assignment.examination_id
        )

        if not exam:
            continue

        results.append({
            "id": exam.id,
            "name": exam.name,
            "course_id": exam.course_id,
            "exam_type": exam.exam_type,
            "duration": exam.duration,
            "max_marks": exam.max_marks,
            "status": exam.status,
            "slot_creation_start": to_ist_string(
                exam.slot_creation_start
            ),
            "slot_creation_end": to_ist_string(
                exam.slot_creation_end
            ),
            "booking_start": to_ist_string(
                exam.booking_start
            ),
            "booking_end": to_ist_string(
                exam.booking_end
            )
        })

    return jsonify({
        "total": len(results),
        "examinations": results
    }), 200


# ==========================================
# VIEW ASSIGNED EXAMINATION RUBRICS
# ==========================================

@examiner_bp.route(
    "/examinations/<int:exam_id>/rubrics",
    methods=["GET"]
)
@role_required("examiner")
def get_assigned_rubrics(exam_id):
    examiner = current_examiner()

    exam = assigned_examination(
        exam_id, examiner.id
    )

    if not exam:
        return jsonify({
            "message": "Examination not assigned"
        }), 404

    rubrics = Rubric.query.filter_by(
        examination_id=exam_id
    ).order_by(Rubric.id).all()

    return jsonify({
        "examination_id": exam_id,
        "rubrics": [
            {
                "id": rubric.id,
                "criterion_name": rubric.criterion_name,
                "max_marks": rubric.max_marks,
                "weightage": rubric.weightage,
                "description": rubric.description
            }
            for rubric in rubrics
        ]
    }), 200


# ==========================================
# CREATE SLOT
# ==========================================

@examiner_bp.route("/slots", methods=["POST"])
@role_required("examiner")
def create_slot():
    examiner = current_examiner()
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    try:
        exam_id = data.get("examination_id")

        if isinstance(exam_id, bool):
            raise ValueError()

        exam_id = int(exam_id)

    except (TypeError, ValueError):
        return jsonify({
            "message": "Valid examination_id is required"
        }), 400

    exam = assigned_examination(
        exam_id, examiner.id
    )

    if not exam:
        return jsonify({
            "message": "Examination not assigned"
        }), 404

    error = slot_creation_error(exam)

    if error:
        return jsonify({"message": error}), 409

    fields, error = validate_slot_data(
        data, exam, examiner.id
    )

    if error:
        return jsonify({"message": error}), 400

    slot = ExaminationSlot(
        examination_id=exam_id,
        examiner_id=examiner.id,
        **fields
    )

    db.session.add(slot)
    db.session.commit()

    return jsonify({
        "message": "Slot created successfully",
        "slot": slot_to_dict(slot)
    }), 201


# ==========================================
# VIEW ALL OWN SLOTS
# ==========================================

@examiner_bp.route("/slots", methods=["GET"])
@role_required("examiner")
def get_slots():
    examiner = current_examiner()

    query = ExaminationSlot.query.filter_by(
        examiner_id=examiner.id
    )

    exam_id = request.args.get(
        "examination_id", type=int
    )

    if exam_id is not None:
        query = query.filter_by(
            examination_id=exam_id
        )

    slots = query.order_by(
        ExaminationSlot.start_time
    ).all()

    return jsonify({
        "total": len(slots),
        "slots": [
            slot_to_dict(slot) for slot in slots
        ]
    }), 200


# ==========================================
# VIEW SINGLE SLOT
# ==========================================

@examiner_bp.route(
    "/slots/<int:slot_id>",
    methods=["GET"]
)
@role_required("examiner")
def get_slot(slot_id):
    examiner = current_examiner()

    slot = get_owned_slot(
        slot_id, examiner.id
    )

    if not slot:
        return jsonify({
            "message": "Slot not found"
        }), 404

    return jsonify({
        "slot": slot_to_dict(slot)
    }), 200


# ==========================================
# UPDATE SLOT
# ==========================================

@examiner_bp.route(
    "/slots/<int:slot_id>",
    methods=["PUT"]
)
@role_required("examiner")
def update_slot(slot_id):
    examiner = current_examiner()

    slot = get_owned_slot(
        slot_id, examiner.id
    )

    if not slot:
        return jsonify({
            "message": "Slot not found"
        }), 404

    exam = assigned_examination(
        slot.examination_id, examiner.id
    )

    if not exam:
        return jsonify({
            "message": "Examination not assigned"
        }), 403

    error = slot_creation_error(exam)

    if error:
        return jsonify({"message": error}), 409

    if slot_has_bookings(slot.id):
        return jsonify({
            "message": (
                "Cannot modify slot after "
                "bookings exist"
            )
        }), 409

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    if "examination_id" in data:
        try:
            requested_exam_id = int(
                data["examination_id"]
            )
        except (TypeError, ValueError):
            return jsonify({
                "message": "Invalid examination_id"
            }), 400

        if requested_exam_id != slot.examination_id:
            return jsonify({
                "message": (
                    "Cannot change slot examination"
                )
            }), 400

    fields, error = validate_slot_data(
        data, exam, examiner.id, slot
    )

    if error:
        return jsonify({"message": error}), 400

    for key, value in fields.items():
        setattr(slot, key, value)

    db.session.commit()

    return jsonify({
        "message": "Slot updated successfully",
        "slot": slot_to_dict(slot)
    }), 200


# ==========================================
# DELETE SLOT
# ==========================================

@examiner_bp.route(
    "/slots/<int:slot_id>",
    methods=["DELETE"]
)
@role_required("examiner")
def delete_slot(slot_id):
    examiner = current_examiner()

    slot = get_owned_slot(
        slot_id, examiner.id
    )

    if not slot:
        return jsonify({
            "message": "Slot not found"
        }), 404

    exam = assigned_examination(
        slot.examination_id, examiner.id
    )

    if not exam:
        return jsonify({
            "message": "Examination not assigned"
        }), 403

    error = slot_creation_error(exam)

    if error:
        return jsonify({"message": error}), 409

    if slot_has_bookings(slot.id):
        return jsonify({
            "message": (
                "Cannot delete slot after "
                "bookings exist"
            )
        }), 409

    db.session.delete(slot)
    db.session.commit()

    return jsonify({
        "message": "Slot deleted successfully"
    }), 200


# ==========================================
# STEP 10 - EXAMINER EVALUATIONS
# ==========================================

from math import isfinite


def get_evaluation_booking(booking_id, examiner_id):
    """Only allow the examiner assigned to the booked slot."""
    booking = db.session.get(Booking, booking_id)

    if booking is None:
        return None

    if booking.status.lower() != "booked":
        return None

    slot = db.session.get(ExaminationSlot, booking.slot_id)

    if slot is None or slot.examiner_id != examiner_id:
        return None

    assignment = ExamAssignment.query.filter_by(
        examination_id=slot.examination_id,
        examiner_id=examiner_id
    ).first()

    if assignment is None:
        return None

    return booking


def evaluation_to_dict(evaluation):
    marks = EvaluationMark.query.filter_by(
        evaluation_id=evaluation.id
    ).order_by(EvaluationMark.rubric_id).all()

    return {
        "id": evaluation.id,
        "booking_id": evaluation.booking_id,
        "examiner_id": evaluation.examiner_id,
        "total_marks": evaluation.total_marks,
        "remarks": evaluation.remarks,
        "status": evaluation.status,
        "is_published": evaluation.is_published,
        "evaluation_date": (
            evaluation.evaluation_date.isoformat()
            if evaluation.evaluation_date else None
        ),
        "marks": [
            {
                "rubric_id": mark.rubric_id,
                "marks_obtained": mark.marks_obtained
            }
            for mark in marks
        ]
    }


@examiner_bp.route(
    "/slots/<int:slot_id>/students",
    methods=["GET"]
)
@role_required("examiner")
def get_slot_students(slot_id):
    examiner = current_examiner()
    slot = get_owned_slot(slot_id, examiner.id)

    if slot is None:
        return jsonify({"message": "Slot not found"}), 404

    bookings = Booking.query.filter(
        Booking.slot_id == slot_id,
        db.func.lower(Booking.status) == "booked"
    ).order_by(Booking.id).all()

    students = []

    for booking in bookings:
        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id
        ).first()

        students.append({
            "booking_id": booking.id,
            "student_id": booking.student_id,
            "student_name": booking.student.name,
            "student_email": booking.student.email,
            "evaluation_id": (
                evaluation.id if evaluation else None
            ),
            "evaluation_status": (
                evaluation.status if evaluation else "Not Started"
            )
        })

    return jsonify({
        "slot_id": slot_id,
        "students": students
    }), 200


@examiner_bp.route(
    "/bookings/<int:booking_id>/evaluation",
    methods=["GET"]
)
@role_required("examiner")
def get_booking_evaluation(booking_id):
    examiner = current_examiner()
    booking = get_evaluation_booking(booking_id, examiner.id)

    if booking is None:
        return jsonify({
            "message": "Active booking not found or access denied"
        }), 404

    slot = db.session.get(ExaminationSlot, booking.slot_id)

    rubrics = Rubric.query.filter_by(
        examination_id=slot.examination_id
    ).order_by(Rubric.id).all()

    evaluation = Evaluation.query.filter_by(
        booking_id=booking.id
    ).first()

    return jsonify({
        "booking_id": booking.id,
        "student_name": booking.student.name,
        "examination_id": slot.examination_id,
        "rubrics": [
            {
                "id": rubric.id,
                "criterion_name": rubric.criterion_name,
                "max_marks": rubric.max_marks,
                "weightage": rubric.weightage
            }
            for rubric in rubrics
        ],
        "evaluation": (
            evaluation_to_dict(evaluation)
            if evaluation else None
        )
    }), 200


@examiner_bp.route(
    "/bookings/<int:booking_id>/evaluation",
    methods=["PUT"]
)
@role_required("examiner")
def save_booking_evaluation(booking_id):
    examiner = current_examiner()
    booking = get_evaluation_booking(booking_id, examiner.id)

    if booking is None:
        return jsonify({
            "message": "Active booking not found or access denied"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Valid JSON is required"}), 400

    submitted_marks = data.get("marks")

    if not isinstance(submitted_marks, list):
        return jsonify({"message": "Marks must be a list"}), 400

    slot = db.session.get(ExaminationSlot, booking.slot_id)

    rubrics = Rubric.query.filter_by(
        examination_id=slot.examination_id
    ).all()

    if not rubrics:
        return jsonify({
            "message": "No rubrics configured"
        }), 409

    rubric_map = {rubric.id: rubric for rubric in rubrics}
    validated_marks = {}
    total = 0.0

    for item in submitted_marks:
        if not isinstance(item, dict):
            return jsonify({"message": "Invalid mark entry"}), 400

        rubric_id = item.get("rubric_id")
        raw_marks = item.get("marks_obtained")

        if type(rubric_id) is not int or rubric_id not in rubric_map:
            return jsonify({"message": "Invalid rubric ID"}), 400

        if rubric_id in validated_marks:
            return jsonify({"message": "Duplicate rubric ID"}), 400

        if type(raw_marks) not in (int, float):
            return jsonify({"message": "Marks must be numeric"}), 400

        marks = float(raw_marks)

        if not isfinite(marks):
            return jsonify({"message": "Marks must be finite"}), 400

        if marks < 0 or marks > rubric_map[rubric_id].max_marks:
            return jsonify({
                "message": "Marks exceed allowed range",
                "rubric_id": rubric_id
            }), 400

        validated_marks[rubric_id] = marks
        total += marks

    if set(validated_marks) != set(rubric_map):
        return jsonify({
            "message": "Marks required for every rubric"
        }), 400

    remarks = data.get("remarks", "")

    if not isinstance(remarks, str):
        return jsonify({"message": "Remarks must be text"}), 400

    evaluation = Evaluation.query.filter_by(
        booking_id=booking.id
    ).first()

    if evaluation and (
        evaluation.status == "Finalized" or evaluation.is_published
    ):
        return jsonify({
            "message": "Finalized or published evaluation cannot be edited"
        }), 409

    try:
        if evaluation is None:
            evaluation = Evaluation(
                booking_id=booking.id,
                examiner_id=examiner.id,
                status="Draft",
                is_published=False
            )
            db.session.add(evaluation)
            db.session.flush()

        EvaluationMark.query.filter_by(
            evaluation_id=evaluation.id
        ).delete(synchronize_session=False)

        for rubric_id, marks in validated_marks.items():
            db.session.add(EvaluationMark(
                evaluation_id=evaluation.id,
                rubric_id=rubric_id,
                marks_obtained=marks
            ))

        evaluation.total_marks = total
        evaluation.remarks = remarks
        evaluation.status = "Draft"
        evaluation.evaluation_date = utc_now()

        db.session.commit()

        return jsonify({
            "message": "Draft evaluation saved",
            "evaluation": evaluation_to_dict(evaluation)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "Could not save evaluation"
        }), 500


@examiner_bp.route(
    "/bookings/<int:booking_id>/evaluation/finalize",
    methods=["PATCH"]
)
@role_required("examiner")
def finalize_booking_evaluation(booking_id):
    examiner = current_examiner()
    booking = get_evaluation_booking(booking_id, examiner.id)

    if booking is None:
        return jsonify({
            "message": "Active booking not found or access denied"
        }), 404

    evaluation = Evaluation.query.filter_by(
        booking_id=booking.id,
        examiner_id=examiner.id
    ).first()

    if evaluation is None:
        return jsonify({
            "message": "Save an evaluation before finalizing"
        }), 409

    if evaluation.status == "Finalized" or evaluation.is_published:
        return jsonify({
            "message": "Evaluation is already finalized or published"
        }), 409

    slot = db.session.get(ExaminationSlot, booking.slot_id)

    rubrics = Rubric.query.filter_by(
        examination_id=slot.examination_id
    ).all()

    marks = EvaluationMark.query.filter_by(
        evaluation_id=evaluation.id
    ).all()

    if not rubrics or {m.rubric_id for m in marks} != {r.id for r in rubrics}:
        return jsonify({
            "message": "Evaluation marks are incomplete"
        }), 409

    try:
        evaluation.status = "Finalized"
        evaluation.evaluation_date = utc_now()
        db.session.commit()

        return jsonify({
            "message": "Evaluation finalized successfully",
            "evaluation": evaluation_to_dict(evaluation)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "Could not finalize evaluation"
        }), 500
