from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from flask import Blueprint, request, jsonify
from models import db, Examination, Rubric
from models import Evaluation, EvaluationMark
from sqlalchemy import func
from routes.auth import role_required

from datetime import datetime, timezone
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from models import (
    db, User, Examination, ExamAssignment,
    ExaminationSlot
)
from routes.auth import role_required

from models import (
    db,
    User,
    Course, 
    Examination,
    ExaminationSlot,
    Booking,
    Rubric,
    ExamAssignment
)
from routes.auth import role_required


admin_bp = Blueprint("admin", __name__)


# Convert a course into JSON
def course_to_dict(course):
    return {
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "description": course.description,
        "status": course.status
    }


# Admin Dashboard
@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def admin_dashboard():
    return jsonify({
        "message": "Welcome to Admin Dashboard",
        "statistics": {
            "total_courses": Course.query.count(),
            "total_examinations": Examination.query.count(),
            "total_students": User.query.filter_by(
                role="student"
            ).count(),
            "total_examiners": User.query.filter_by(
                role="examiner"
            ).count(),
            "total_slots": ExaminationSlot.query.count(),
            "total_bookings": Booking.query.count(),
            "active_bookings": Booking.query.filter_by(
                status="booked"
            ).count(),
            "total_evaluations": Evaluation.query.count(),
            "draft_evaluations": Evaluation.query.filter_by(
                status="Draft"
            ).count(),
            "finalized_evaluations": Evaluation.query.filter_by(
                status="Finalized"
            ).count(),
            "published_results": Evaluation.query.filter_by(
                is_published=True
            ).count()
        }
    }), 200

# CREATE COURSE
@admin_bp.route("/courses", methods=["POST"])
@role_required("admin")
def create_course():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    code = str(data.get("code") or "").strip().upper()
    name = str(data.get("name") or "").strip()
    description = str(data.get("description") or "").strip()
    status = str(data.get("status") or "active").strip().lower()

    if not code or not name:
        return jsonify({
            "message": "Course code and name are required"
        }), 400

    if len(code) > 20 or len(name) > 100:
        return jsonify({
            "message": "Course code or name is too long"
        }), 400

    if status not in ["active", "inactive"]:
        return jsonify({
            "message": "Status must be active or inactive"
        }), 400

    existing_course = Course.query.filter_by(code=code).first()

    if existing_course:
        return jsonify({
            "message": "Course code already exists"
        }), 409

    course = Course(
        code=code,
        name=name,
        description=description,
        status=status
    )

    db.session.add(course)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Course code already exists"
        }), 409

    return jsonify({
        "message": "Course created successfully",
        "course": course_to_dict(course)
    }), 201


# VIEW ALL COURSES AND SEARCH
@admin_bp.route("/courses", methods=["GET"])
@role_required("admin")
def get_courses():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip().lower()

    query = Course.query

    if search:
        query = query.filter(
            db.or_(
                Course.code.ilike(f"%{search}%"),
                Course.name.ilike(f"%{search}%")
            )
        )

    if status:
        if status not in ["active", "inactive"]:
            return jsonify({
                "message": "Invalid status filter"
            }), 400

        query = query.filter_by(status=status)

    courses = query.order_by(Course.id.desc()).all()

    return jsonify({
        "total": len(courses),
        "courses": [
            course_to_dict(course) for course in courses
        ]
    }), 200


# VIEW A SINGLE COURSE
@admin_bp.route("/courses/<int:course_id>", methods=["GET"])
@role_required("admin")
def get_course(course_id):
    course = db.get_or_404(Course, course_id)

    return jsonify({
        "course": course_to_dict(course)
    }), 200


# UPDATE COURSE
@admin_bp.route("/courses/<int:course_id>", methods=["PUT"])
@role_required("admin")
def update_course(course_id):
    course = db.get_or_404(Course, course_id)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    code = str(data.get("code", course.code) or "").strip().upper()
    name = str(data.get("name", course.name) or "").strip()
    description = str(
        data.get("description", course.description) or ""
    ).strip()
    status = str(
        data.get("status", course.status) or ""
    ).strip().lower()

    if not code or not name:
        return jsonify({
            "message": "Course code and name are required"
        }), 400

    if len(code) > 20 or len(name) > 100:
        return jsonify({
            "message": "Course code or name is too long"
        }), 400

    if status not in ["active", "inactive"]:
        return jsonify({
            "message": "Status must be active or inactive"
        }), 400

    duplicate = Course.query.filter(
        Course.code == code,
        Course.id != course_id
    ).first()

    if duplicate:
        return jsonify({
            "message": "Another course uses this code"
        }), 409

    course.code = code
    course.name = name
    course.description = description
    course.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Course code already exists"
        }), 409

    return jsonify({
        "message": "Course updated successfully",
        "course": course_to_dict(course)
    }), 200


# DELETE COURSE
@admin_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@role_required("admin")
def delete_course(course_id):
    course = db.get_or_404(Course, course_id)

    # Protect examination history
    exam_count = Examination.query.filter_by(
        course_id=course.id
    ).count()

    if exam_count > 0:
        return jsonify({
            "message": (
                "Cannot delete a course that has examinations. "
                "Set its status to inactive instead."
            )
        }), 409

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "message": "Course deleted successfully"
    }), 200



# ============================================
# EXAMINATION MANAGEMENT
# ============================================

EXAM_TYPES = {
    "Viva", "Practical", "Project Demo", "Assessment"
}

EXAM_STATUSES = {
    "Draft", "Slot Creation", "Booking Open",
    "Closed", "Completed"
}

DATE_FIELDS = (
    "slot_creation_start",
    "slot_creation_end",
    "booking_start",
    "booking_end"
)


def examination_to_dict(exam):
    return {
        "id": exam.id,
        "course_id": exam.course_id,
        "course_name": exam.course.name,
        "name": exam.name,
        "exam_type": exam.exam_type,
        "duration": exam.duration,
        "max_marks": exam.max_marks,
        "slot_creation_start": (
            exam.slot_creation_start.isoformat()
            if exam.slot_creation_start else None
        ),
        "slot_creation_end": (
            exam.slot_creation_end.isoformat()
            if exam.slot_creation_end else None
        ),
        "booking_start": (
            exam.booking_start.isoformat()
            if exam.booking_start else None
        ),
        "booking_end": (
            exam.booking_end.isoformat()
            if exam.booking_end else None
        ),
        "status": exam.status
    }


def parse_exam_datetime(value):
    """
    Accept ISO dates such as 2026-12-01T09:00:00.
    For this local project, all naive dates are
    interpreted as Asia/Kolkata local time.

    Store values as naive UTC in SQLite.
    """
    from zoneinfo import ZoneInfo

    if not isinstance(value, str):
        raise ValueError("Date must be an ISO date string")

    parsed = datetime.fromisoformat(
        value.strip().replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=ZoneInfo("Asia/Kolkata")
        )

    return parsed.astimezone(
        timezone.utc
    ).replace(tzinfo=None)


def validate_exam_data(data, existing=None):
    """
    Validate create/update requests.
    Returns (validated_fields, error_message).
    """
    if not isinstance(data, dict):
        return None, "Valid JSON data is required"

    fields = {}

    course_id = data.get(
        "course_id",
        existing.course_id if existing else None
    )

    try:
        if isinstance(course_id, bool):
            raise ValueError()
        course_id = int(course_id)
    except (TypeError, ValueError):
        return None, "Valid course_id is required"

    course = db.session.get(Course, course_id)

    if not course:
        return None, "Course does not exist"

    if course.status != "active":
        return None, "Course must be active"

    fields["course_id"] = course_id

    name = data.get(
        "name",
        existing.name if existing else ""
    )

    if not isinstance(name, str) or not name.strip():
        return None, "Examination name is required"

    if len(name.strip()) > 100:
        return None, "Examination name is too long"

    fields["name"] = name.strip()

    exam_type = data.get(
        "exam_type",
        existing.exam_type if existing else None
    )

    if exam_type not in EXAM_TYPES:
        return None, (
            "Exam type must be Viva, Practical, "
            "Project Demo or Assessment"
        )

    fields["exam_type"] = exam_type

    for key in ("duration", "max_marks"):
        value = data.get(
            key,
            getattr(existing, key) if existing else None
        )

        try:
            if isinstance(value, bool):
                raise ValueError()
            number = int(value)
            if str(value).strip() != str(number):
                raise ValueError()
        except (TypeError, ValueError):
            return None, f"{key} must be an integer"

        if number <= 0:
            return None, f"{key} must be greater than zero"

        fields[key] = number

    for key in DATE_FIELDS:
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
                fields[key] = parse_exam_datetime(value)
            except (ValueError, TypeError):
                return None, f"Invalid date: {key}"

    if fields["slot_creation_start"] >= fields["slot_creation_end"]:
        return None, "Invalid slot creation timeline"

    if fields["booking_start"] >= fields["booking_end"]:
        return None, "Invalid booking timeline"

    if fields["slot_creation_end"] > fields["booking_start"]:
        return None, (
            "Slot creation must end before "
            "student booking begins"
        )

    status = data.get(
        "status",
        existing.status if existing else "Draft"
    )

    if status not in EXAM_STATUSES:
        return None, "Invalid examination status"

    fields["status"] = status

    return fields, None


def exam_status_error(exam, new_status):
    """
    Basic lifecycle validation.
    A completed examination cannot be reopened.
    """
    allowed = {
        "Draft": {"Draft", "Slot Creation"},
        "Slot Creation": {
            "Slot Creation", "Booking Open", "Closed"
        },
        "Booking Open": {"Booking Open", "Closed"},
        "Closed": {"Closed", "Completed"},
        "Completed": {"Completed"}
    }

    if new_status not in allowed.get(exam.status, set()):
        return "Invalid examination status transition"

    return None


# --------------------------------------------
# CREATE EXAMINATION
# --------------------------------------------

@admin_bp.route("/examinations", methods=["POST"])
@role_required("admin")
def create_examination():
    data = request.get_json(silent=True)

    fields, error = validate_exam_data(data)

    if error:
        return jsonify({"message": error}), 400

    # New examinations must begin in Draft.
    if fields["status"] != "Draft":
        return jsonify({
            "message": "New examinations must start in Draft"
        }), 400

    exam = Examination(**fields)

    db.session.add(exam)
    db.session.commit()

    return jsonify({
        "message": "Examination created successfully",
        "examination": examination_to_dict(exam)
    }), 201


# --------------------------------------------
# VIEW AND SEARCH EXAMINATIONS
# --------------------------------------------

@admin_bp.route("/examinations", methods=["GET"])
@role_required("admin")
def get_examinations():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    course_id = request.args.get("course_id", type=int)

    query = Examination.query.join(Course)

    if search:
        query = query.filter(
            db.or_(
                Examination.name.ilike(f"%{search}%"),
                Course.name.ilike(f"%{search}%"),
                Course.code.ilike(f"%{search}%")
            )
        )

    if status:
        if status not in EXAM_STATUSES:
            return jsonify({
                "message": "Invalid status filter"
            }), 400
        query = query.filter(Examination.status == status)

    if course_id is not None:
        query = query.filter(
            Examination.course_id == course_id
        )

    exams = query.order_by(
        Examination.id.desc()
    ).all()

    return jsonify({
        "total": len(exams),
        "examinations": [
            examination_to_dict(exam) for exam in exams
        ]
    }), 200


# --------------------------------------------
# VIEW SINGLE EXAMINATION
# --------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>",
    methods=["GET"]
)
@role_required("admin")
def get_examination(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    return jsonify({
        "examination": examination_to_dict(exam)
    }), 200


# --------------------------------------------
# UPDATE EXAMINATION
# --------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_examination(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    fields, error = validate_exam_data(data, exam)

    if error:
        return jsonify({"message": error}), 400

    # Protect history after bookings or evaluations exist.
    has_bookings = (
        db.session.query(Booking.id)
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(ExaminationSlot.examination_id == exam_id)
        .first() is not None
    )

    if has_bookings:
        protected = (
            "course_id", "duration", "max_marks",
            "slot_creation_start", "slot_creation_end",
            "booking_start", "booking_end"
        )

        for key in protected:
            if fields[key] != getattr(exam, key):
                return jsonify({
                    "message": (
                        f"Cannot change {key} after "
                        "bookings exist"
                    )
                }), 409

    # Changing status is handled by a separate endpoint.
    if fields["status"] != exam.status:
        return jsonify({
            "message": (
                "Use the status endpoint to change "
                "examination status"
            )
        }), 400

    if exam.status == "Completed":
        return jsonify({
            "message": "Completed examinations cannot be edited"
        }), 409

    for key, value in fields.items():
        setattr(exam, key, value)

    db.session.commit()

    return jsonify({
        "message": "Examination updated successfully",
        "examination": examination_to_dict(exam)
    }), 200


# --------------------------------------------
# CHANGE EXAMINATION STATUS
# --------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def change_examination_status(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    new_status = data.get("status")

    if new_status not in EXAM_STATUSES:
        return jsonify({
            "message": "Invalid examination status"
        }), 400

    error = exam_status_error(exam, new_status)

    if error:
        return jsonify({"message": error}), 409

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if new_status == "Slot Creation":
        if not (
            exam.slot_creation_start <= now
            <= exam.slot_creation_end
        ):
            return jsonify({
                "message": (
                    "Outside the slot creation period"
                )
            }), 409

    if new_status == "Booking Open":
        if not (
            exam.booking_start <= now <= exam.booking_end
        ):
            return jsonify({
                "message": "Outside the booking period"
            }), 409

    if new_status == "Completed":
        if now < exam.booking_end:
            return jsonify({
                "message": (
                    "Cannot complete before booking closes"
                )
            }), 409

    exam.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Examination status updated",
        "examination": examination_to_dict(exam)
    }), 200


# --------------------------------------------
# DELETE EXAMINATION
# --------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_examination(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    if exam.status != "Draft":
        return jsonify({
            "message": "Only Draft examinations can be deleted"
        }), 409

    slot_count = ExaminationSlot.query.filter_by(
        examination_id=exam_id
    ).count()

    rubric_count = Rubric.query.filter_by(
        examination_id=exam_id
    ).count()

    assignment_count = ExamAssignment.query.filter_by(
        examination_id=exam_id
    ).count()

    if slot_count or rubric_count or assignment_count:
        return jsonify({
            "message": (
                "Cannot delete examination with slots, "
                "rubrics or examiner assignments"
            )
        }), 409

    db.session.delete(exam)
    db.session.commit()

    return jsonify({
        "message": "Examination deleted successfully"
    }), 200


# ==========================================
# STEP 6: ADMIN RUBRIC MANAGEMENT
# ==========================================

def rubric_to_dict(rubric):
    return {
        "id": rubric.id,
        "examination_id": rubric.examination_id,
        "criterion_name": rubric.criterion_name,
        "max_marks": rubric.max_marks,
        "weightage": rubric.weightage,
        "description": rubric.description
    }


def rubric_has_evaluations(exam_id):
    """Check whether an exam already has evaluations."""
    from models import Evaluation, Booking, ExaminationSlot

    return (
        db.session.query(Evaluation.id)
        .join(Booking, Evaluation.booking_id == Booking.id)
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(ExaminationSlot.examination_id == exam_id)
        .first() is not None
    )


def validate_rubric(data, exam, existing=None):
    """Validate rubric fields and examination totals."""

    if not isinstance(data, dict):
        return None, "Valid JSON data is required"

    criterion = data.get(
        "criterion_name",
        existing.criterion_name if existing else None
    )

    if not isinstance(criterion, str) or not criterion.strip():
        return None, "Criterion name is required"

    criterion = criterion.strip()

    if len(criterion) > 100:
        return None, "Criterion name is too long"

    description = data.get(
        "description",
        existing.description if existing else ""
    )

    if description is None:
        description = ""

    if not isinstance(description, str):
        return None, "Description must be text"

    if len(description) > 1000:
        return None, "Description is too long"

    try:
        marks = data.get(
            "max_marks",
            existing.max_marks if existing else None
        )

        if isinstance(marks, bool):
            raise ValueError()

        marks = int(marks)

        if marks <= 0:
            raise ValueError()

    except (ValueError, TypeError):
        return None, "max_marks must be a positive integer"

    try:
        weightage = data.get(
            "weightage",
            existing.weightage if existing else None
        )

        if isinstance(weightage, bool):
            raise ValueError()

        weightage = float(weightage)

        import math
        if not math.isfinite(weightage):
            raise ValueError()

        if weightage <= 0 or weightage > 100:
            raise ValueError()

    except (ValueError, TypeError):
        return None, "weightage must be between 0 and 100"

    other_rubrics = Rubric.query.filter_by(
        examination_id=exam.id
    ).all()

    other_rubrics = [
        r for r in other_rubrics
        if existing is None or r.id != existing.id
    ]

    # Prevent duplicate criterion names.
    for rubric in other_rubrics:
        if rubric.criterion_name.casefold() == criterion.casefold():
            return None, "Criterion already exists"

    total_marks = marks + sum(
        r.max_marks for r in other_rubrics
    )

    if total_marks > exam.max_marks:
        return None, (
            f"Rubric marks exceed examination "
            f"maximum of {exam.max_marks}"
        )

    total_weightage = weightage + sum(
        r.weightage for r in other_rubrics
    )

    if total_weightage > 100.000001:
        return None, "Total rubric weightage cannot exceed 100%"

    return {
        "criterion_name": criterion,
        "max_marks": marks,
        "weightage": weightage,
        "description": description
    }, None


def rubric_summary(exam):
    rubrics = Rubric.query.filter_by(
        examination_id=exam.id
    ).order_by(Rubric.id).all()

    total_marks = sum(r.max_marks for r in rubrics)
    total_weightage = sum(r.weightage for r in rubrics)

    return {
        "examination_id": exam.id,
        "examination_name": exam.name,
        "examination_max_marks": exam.max_marks,
        "total_rubric_marks": total_marks,
        "total_weightage": round(total_weightage, 4),
        "remaining_marks": exam.max_marks - total_marks,
        "remaining_weightage": round(
            100 - total_weightage, 4
        ),
        "is_complete": (
            total_marks == exam.max_marks
            and abs(total_weightage - 100) < 0.000001
        ),
        "rubrics": [rubric_to_dict(r) for r in rubrics]
    }


# ------------------------------------------
# CREATE RUBRIC
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/rubrics",
    methods=["POST"]
)
@role_required("admin")
def create_rubric(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    if exam.status not in ("Draft", "Slot Creation"):
        return jsonify({
            "message": "Rubrics cannot be added at this stage"
        }), 409

    if rubric_has_evaluations(exam_id):
        return jsonify({
            "message": "Cannot change rubrics after evaluations exist"
        }), 409

    data = request.get_json(silent=True)

    fields, error = validate_rubric(data, exam)

    if error:
        return jsonify({"message": error}), 400

    rubric = Rubric(
        examination_id=exam_id,
        **fields
    )

    db.session.add(rubric)
    db.session.commit()

    return jsonify({
        "message": "Rubric created successfully",
        "rubric": rubric_to_dict(rubric),
        "summary": rubric_summary(exam)
    }), 201


# ------------------------------------------
# VIEW ALL RUBRICS FOR AN EXAMINATION
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/rubrics",
    methods=["GET"]
)
@role_required("admin")
def get_rubrics(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    return jsonify(rubric_summary(exam)), 200


# ------------------------------------------
# VIEW SINGLE RUBRIC
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/rubrics/<int:rubric_id>",
    methods=["GET"]
)
@role_required("admin")
def get_rubric(exam_id, rubric_id):
    db.get_or_404(Examination, exam_id)

    rubric = Rubric.query.filter_by(
        id=rubric_id,
        examination_id=exam_id
    ).first_or_404()

    return jsonify({
        "rubric": rubric_to_dict(rubric)
    }), 200


# ------------------------------------------
# UPDATE RUBRIC
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/rubrics/<int:rubric_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_rubric(exam_id, rubric_id):
    exam = db.get_or_404(Examination, exam_id)

    rubric = Rubric.query.filter_by(
        id=rubric_id,
        examination_id=exam_id
    ).first_or_404()

    if exam.status not in ("Draft", "Slot Creation"):
        return jsonify({
            "message": "Rubrics cannot be edited at this stage"
        }), 409

    if rubric_has_evaluations(exam_id):
        return jsonify({
            "message": "Cannot edit rubrics after evaluations exist"
        }), 409

    data = request.get_json(silent=True)

    fields, error = validate_rubric(data, exam, rubric)

    if error:
        return jsonify({"message": error}), 400

    for key, value in fields.items():
        setattr(rubric, key, value)

    db.session.commit()

    return jsonify({
        "message": "Rubric updated successfully",
        "rubric": rubric_to_dict(rubric),
        "summary": rubric_summary(exam)
    }), 200


# ------------------------------------------
# DELETE RUBRIC
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/rubrics/<int:rubric_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_rubric(exam_id, rubric_id):
    exam = db.get_or_404(Examination, exam_id)

    rubric = Rubric.query.filter_by(
        id=rubric_id,
        examination_id=exam_id
    ).first_or_404()

    if exam.status not in ("Draft", "Slot Creation"):
        return jsonify({
            "message": "Rubrics cannot be deleted at this stage"
        }), 409

    if rubric_has_evaluations(exam_id):
        return jsonify({
            "message": "Cannot delete rubrics after evaluations exist"
        }), 409

    db.session.delete(rubric)
    db.session.commit()

    return jsonify({
        "message": "Rubric deleted successfully",
        "summary": rubric_summary(exam)
    }), 200


# ==========================================
# STEP 7: ADMIN EXAMINER MANAGEMENT
# ==========================================

def examiner_to_dict(examiner):
    return {
        "id": examiner.id,
        "name": examiner.name,
        "email": examiner.email,
        "role": examiner.role,
        "department": examiner.department,
        "contact": examiner.contact,
        "status": examiner.status
    }


def assignment_to_dict(assignment):
    return {
        "id": assignment.id,
        "examination_id": assignment.examination_id,
        "examiner_id": assignment.examiner_id
    }


def validate_examiner_data(data, existing=None):
    if not isinstance(data, dict):
        return None, "Valid JSON data is required"

    fields = {}

    name = data.get(
        "name",
        existing.name if existing else ""
    )

    if not isinstance(name, str) or not name.strip():
        return None, "Examiner name is required"

    if len(name.strip()) > 100:
        return None, "Name must not exceed 100 characters"

    fields["name"] = name.strip()

    email = data.get(
        "email",
        existing.email if existing else ""
    )

    if not isinstance(email, str):
        return None, "Valid email is required"

    email = email.strip().lower()

    if (
        not email
        or "@" not in email
        or "." not in email.split("@")[-1]
        or len(email) > 255
    ):
        return None, "Valid email is required"

    duplicate = User.query.filter(
        db.func.lower(User.email) == email
    ).first()

    if duplicate and (
        existing is None or duplicate.id != existing.id
    ):
        return None, "Email already registered"

    fields["email"] = email

    department = data.get(
        "department",
        existing.department if existing else ""
    )

    if department is None:
        department = ""

    if not isinstance(department, str):
        return None, "Department must be text"

    if len(department.strip()) > 100:
        return None, "Department is too long"

    fields["department"] = department.strip()

    contact = data.get(
        "contact",
        existing.contact if existing else ""
    )

    if contact is None:
        contact = ""

    if not isinstance(contact, str):
        return None, "Contact must be text"

    if len(contact.strip()) > 30:
        return None, "Contact is too long"

    fields["contact"] = contact.strip()

    if existing is None:
        password = data.get("password")

        if not isinstance(password, str) or len(password) < 8:
            return None, (
                "Password must contain at least 8 characters"
            )

        fields["password"] = generate_password_hash(
            password
        )

    elif "password" in data:
        password = data["password"]

        if not isinstance(password, str) or len(password) < 8:
            return None, (
                "Password must contain at least 8 characters"
            )

        fields["password"] = generate_password_hash(
            password
        )

    return fields, None


def examiner_has_upcoming_slots(examiner_id):
    now = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    return (
        ExaminationSlot.query.filter(
            ExaminationSlot.examiner_id == examiner_id,
            ExaminationSlot.start_time > now,
            ExaminationSlot.status == "active"
        ).first() is not None
    )


# ------------------------------------------
# CREATE EXAMINER
# ------------------------------------------

@admin_bp.route("/examiners", methods=["POST"])
@role_required("admin")
def create_examiner():
    data = request.get_json(silent=True)

    fields, error = validate_examiner_data(data)

    if error:
        return jsonify({"message": error}), 400

    examiner = User(
        **fields,
        role="examiner",
        status="active"
    )

    db.session.add(examiner)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Email already registered"
        }), 409

    return jsonify({
        "message": "Examiner created successfully",
        "examiner": examiner_to_dict(examiner)
    }), 201


# ------------------------------------------
# VIEW ALL EXAMINERS
# ------------------------------------------

@admin_bp.route("/examiners", methods=["GET"])
@role_required("admin")
def get_examiners():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = User.query.filter_by(role="examiner")

    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.department.ilike(f"%{search}%")
            )
        )

    if status:
        if status not in ("active", "inactive"):
            return jsonify({
                "message": "Invalid status filter"
            }), 400

        query = query.filter(User.status == status)

    examiners = query.order_by(User.id.desc()).all()

    return jsonify({
        "total": len(examiners),
        "examiners": [
            examiner_to_dict(e) for e in examiners
        ]
    }), 200


# ------------------------------------------
# VIEW SINGLE EXAMINER
# ------------------------------------------

@admin_bp.route(
    "/examiners/<int:examiner_id>",
    methods=["GET"]
)
@role_required("admin")
def get_examiner(examiner_id):
    examiner = User.query.filter_by(
        id=examiner_id,
        role="examiner"
    ).first_or_404()

    return jsonify({
        "examiner": examiner_to_dict(examiner)
    }), 200


# ------------------------------------------
# UPDATE EXAMINER
# ------------------------------------------

@admin_bp.route(
    "/examiners/<int:examiner_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_examiner(examiner_id):
    examiner = User.query.filter_by(
        id=examiner_id,
        role="examiner"
    ).first_or_404()

    data = request.get_json(silent=True)

    fields, error = validate_examiner_data(
        data, examiner
    )

    if error:
        return jsonify({"message": error}), 400

    for key, value in fields.items():
        setattr(examiner, key, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Email already registered"
        }), 409

    return jsonify({
        "message": "Examiner updated successfully",
        "examiner": examiner_to_dict(examiner)
    }), 200


# ------------------------------------------
# ACTIVATE / DEACTIVATE EXAMINER
# ------------------------------------------

@admin_bp.route(
    "/examiners/<int:examiner_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def change_examiner_status(examiner_id):
    examiner = User.query.filter_by(
        id=examiner_id,
        role="examiner"
    ).first_or_404()

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    new_status = data.get("status")

    if new_status not in ("active", "inactive"):
        return jsonify({
            "message": "Status must be active or inactive"
        }), 400

    if (
        new_status == "inactive"
        and examiner_has_upcoming_slots(examiner_id)
    ):
        return jsonify({
            "message": (
                "Cannot deactivate examiner with "
                "upcoming active slots"
            )
        }), 409

    examiner.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Examiner status updated successfully",
        "examiner": examiner_to_dict(examiner)
    }), 200


# ==========================================
# EXAMINATION ASSIGNMENTS
# ==========================================

# ------------------------------------------
# ASSIGN EXAMINER TO EXAMINATION
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/assignments",
    methods=["POST"]
)
@role_required("admin")
def assign_examiner(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    if exam.status in ("Closed", "Completed"):
        return jsonify({
            "message": (
                "Cannot assign examiners to "
                "closed or completed examinations"
            )
        }), 409

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    examiner_id = data.get("examiner_id")

    try:
        if isinstance(examiner_id, bool):
            raise ValueError()
        examiner_id = int(examiner_id)
    except (ValueError, TypeError):
        return jsonify({
            "message": "Valid examiner_id is required"
        }), 400

    examiner = User.query.filter_by(
        id=examiner_id,
        role="examiner"
    ).first()

    if not examiner:
        return jsonify({
            "message": "Examiner not found"
        }), 404

    if examiner.status != "active":
        return jsonify({
            "message": "Examiner must be active"
        }), 409

    existing = ExamAssignment.query.filter_by(
        examination_id=exam_id,
        examiner_id=examiner_id
    ).first()

    if existing:
        return jsonify({
            "message": "Examiner already assigned"
        }), 409

    assignment = ExamAssignment(
        examination_id=exam_id,
        examiner_id=examiner_id
    )

    db.session.add(assignment)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Examiner already assigned"
        }), 409

    return jsonify({
        "message": "Examiner assigned successfully",
        "assignment": assignment_to_dict(assignment)
    }), 201


# ------------------------------------------
# VIEW EXAMINATION ASSIGNMENTS
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/assignments",
    methods=["GET"]
)
@role_required("admin")
def get_exam_assignments(exam_id):
    exam = db.get_or_404(Examination, exam_id)

    assignments = ExamAssignment.query.filter_by(
        examination_id=exam_id
    ).order_by(ExamAssignment.id).all()

    results = []

    for assignment in assignments:
        examiner = db.session.get(
            User, assignment.examiner_id
        )

        results.append({
            "id": assignment.id,
            "examination_id": exam_id,
            "examiner_id": assignment.examiner_id,
            "examiner_name": (
                examiner.name if examiner else None
            ),
            "examiner_email": (
                examiner.email if examiner else None
            ),
            "examiner_status": (
                examiner.status if examiner else None
            )
        })

    return jsonify({
        "examination_id": exam.id,
        "examination_name": exam.name,
        "total": len(results),
        "assignments": results
    }), 200


# ------------------------------------------
# REMOVE EXAMINER ASSIGNMENT
# ------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/assignments/<int:assignment_id>",
    methods=["DELETE"]
)
@role_required("admin")
def remove_exam_assignment(exam_id, assignment_id):
    exam = db.get_or_404(Examination, exam_id)

    assignment = ExamAssignment.query.filter_by(
        id=assignment_id,
        examination_id=exam_id
    ).first_or_404()

    if exam.status in ("Closed", "Completed"):
        return jsonify({
            "message": (
                "Cannot remove assignments from "
                "closed or completed examinations"
            )
        }), 409

    existing_slot = ExaminationSlot.query.filter_by(
        examination_id=exam_id,
        examiner_id=assignment.examiner_id
    ).first()

    if existing_slot:
        return jsonify({
            "message": (
                "Cannot unassign examiner while "
                "examination slots exist"
            )
        }), 409

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({
        "message": "Examiner assignment removed successfully"
    }), 200

# ============================================================
# STEP 11 - ADMIN RESULTS MANAGEMENT
# ============================================================

def admin_result_to_dict(evaluation):
    booking = db.session.get(Booking, evaluation.booking_id)
    slot = db.session.get(ExaminationSlot, booking.slot_id)
    student = db.session.get(User, booking.student_id)

    marks = EvaluationMark.query.filter_by(
        evaluation_id=evaluation.id
    ).all()

    return {
        "evaluation_id": evaluation.id,
        "booking_id": booking.id,
        "examination_id": slot.examination_id,
        "student_id": student.id,
        "student_name": student.name,
        "student_email": student.email,
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


# ------------------------------------------------------------
# GET ALL RESULTS FOR AN EXAMINATION
# ------------------------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/results",
    methods=["GET"]
)
@role_required("admin")
def get_examination_results(exam_id):

    exam = db.get_or_404(Examination, exam_id)

    evaluations = (
        Evaluation.query
        .join(
            Booking,
            Evaluation.booking_id == Booking.id
        )
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(
            ExaminationSlot.examination_id == exam_id
        )
        .order_by(Evaluation.id)
        .all()
    )

    return jsonify({
        "examination_id": exam.id,
        "examination_name": exam.name,
        "total_evaluations": len(evaluations),
        "results": [
            admin_result_to_dict(evaluation)
            for evaluation in evaluations
        ]
    }), 200


# ------------------------------------------------------------
# PUBLISH FINALIZED RESULTS
# ------------------------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/results/publish",
    methods=["PATCH"]
)
@role_required("admin")
def publish_examination_results(exam_id):

    exam = db.get_or_404(Examination, exam_id)

    active_bookings = (
        Booking.query
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(
            ExaminationSlot.examination_id == exam_id,
            Booking.status == "booked"
        )
        .all()
    )

    if not active_bookings:
        return jsonify({
            "message": "No active bookings to publish"
        }), 409

    incomplete_booking_ids = []

    for booking in active_bookings:
        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id
        ).first()

        if evaluation is None or evaluation.status != "Finalized":
            incomplete_booking_ids.append(booking.id)

    if incomplete_booking_ids:
        return jsonify({
            "message": "All active bookings must have finalized evaluations",
            "incomplete_booking_ids": incomplete_booking_ids
        }), 409
    evaluations = (
        Evaluation.query
        .join(
            Booking,
            Evaluation.booking_id == Booking.id
        )
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(
            ExaminationSlot.examination_id == exam_id
        )
        .all()
    )

    if not evaluations:
        return jsonify({
            "message": "No evaluations available to publish"
        }), 409

    incomplete = [
        evaluation.id
        for evaluation in evaluations
        if evaluation.status != "Finalized"
        and not (
            evaluation.status == "Finalized"
            and evaluation.is_published
        )
    ]

    if incomplete:
        return jsonify({
            "message": "All evaluations must be finalized before publishing",
            "incomplete_evaluation_ids": incomplete
        }), 409

    published_count = 0

    for evaluation in evaluations:
        if not evaluation.is_published:
            evaluation.is_published = True
            published_count += 1

    db.session.commit()

    return jsonify({
        "message": "Results published successfully",
        "examination_id": exam.id,
        "newly_published": published_count,
        "total_evaluations": len(evaluations)
    }), 200


# ------------------------------------------------------------
# EXAMINATION RESULTS SUMMARY
# ------------------------------------------------------------

@admin_bp.route(
    "/examinations/<int:exam_id>/results/summary",
    methods=["GET"]
)
@role_required("admin")
def examination_results_summary(exam_id):

    exam = db.get_or_404(Examination, exam_id)

    evaluations = (
        Evaluation.query
        .join(
            Booking,
            Evaluation.booking_id == Booking.id
        )
        .join(
            ExaminationSlot,
            Booking.slot_id == ExaminationSlot.id
        )
        .filter(
            ExaminationSlot.examination_id == exam_id
        )
        .all()
    )

    finalized = [
        evaluation
        for evaluation in evaluations
        if evaluation.status == "Finalized"
    ]

    published = [
        evaluation
        for evaluation in evaluations
        if evaluation.is_published
    ]

    marks = [
        evaluation.total_marks
        for evaluation in finalized
        if evaluation.total_marks is not None
    ]

    return jsonify({
        "examination_id": exam.id,
        "examination_name": exam.name,
        "maximum_marks": exam.max_marks,
        "total_evaluations": len(evaluations),
        "finalized_evaluations": len(finalized),
        "published_evaluations": len(published),
        "average_marks": (
            round(sum(marks) / len(marks), 2)
            if marks else None
        ),
        "highest_marks": max(marks) if marks else None,
        "lowest_marks": min(marks) if marks else None
    }), 200
