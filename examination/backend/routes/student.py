
import sqlite3
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, request, session
from models import Evaluation, EvaluationMark, Rubric
from models import (
    db,
    User,
    Examination,
    ExaminationSlot,
    Booking
)
from routes.auth import role_required


student_bp = Blueprint("student", __name__)

IST = ZoneInfo("Asia/Kolkata")

ACTIVE_BOOKING = "booked"
CANCELLED_BOOKING = "cancelled"

CLOSED_EXAM_STATUSES = {
    "draft", "closed", "completed", "cancelled"
}


# ==========================================
# HELPERS
# ==========================================

def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def now_ist():
    return datetime.now(IST).replace(tzinfo=None)


def current_student():
    return db.session.get(User, session.get("user_id"))


def booking_count(slot_id):
    return Booking.query.filter_by(
        slot_id=slot_id,
        status=ACTIVE_BOOKING
    ).count()


def exam_is_bookable(exam):
    if exam.status.strip().lower() in CLOSED_EXAM_STATUSES:
        return False

    if not exam.booking_start or not exam.booking_end:
        return False

    # Examination administrative dates are stored
    # as naive India-local datetimes by the admin API.
    now = now_utc()

    return exam.booking_start <= now <= exam.booking_end


def slot_is_bookable(slot):
    return (
        slot.status == "active"
        and slot.start_time > now_utc()
    )


def slot_to_dict(slot):
    exam = db.session.get(
        Examination, slot.examination_id
    )

    booked = booking_count(slot.id)

    return {
        "id": slot.id,
        "examination_id": slot.examination_id,
        "examination_name": exam.name if exam else None,
        "examiner_id": slot.examiner_id,
        "start_time": (
            slot.start_time.replace(tzinfo=timezone.utc)
            .astimezone(IST).isoformat()
        ),
        "end_time": (
            slot.end_time.replace(tzinfo=timezone.utc)
            .astimezone(IST).isoformat()
        ),
        "capacity": slot.capacity,
        "booked_count": booked,
        "available_seats": max(0, slot.capacity - booked),
        "status": slot.status,
        "booking_open": (
            exam_is_bookable(exam) if exam else False
        )
    }


def booking_to_dict(booking):
    slot = db.session.get(
        ExaminationSlot, booking.slot_id
    )

    exam = (
        db.session.get(Examination, slot.examination_id)
        if slot else None
    )

    return {
        "id": booking.id,
        "student_id": booking.student_id,
        "slot_id": booking.slot_id,
        "examination_id": exam.id if exam else None,
        "examination_name": exam.name if exam else None,
        "status": booking.status,
        "booking_date": (
            booking.booking_date.isoformat()
            if booking.booking_date else None
        ),
        "start_time": (
            slot.start_time.replace(tzinfo=timezone.utc)
            .astimezone(IST).isoformat()
            if slot else None
        ),
        "end_time": (
            slot.end_time.replace(tzinfo=timezone.utc)
            .astimezone(IST).isoformat()
            if slot else None
        )
    }


def sqlite_connection():
    """
    Dedicated SQLite connection for atomic booking
    and cancellation transactions.

    This application uses SQLite only.
    """
    database_path = db.engine.url.database

    conn = sqlite3.connect(
        database_path,
        timeout=15,
        isolation_level=None
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")

    return conn


def parse_db_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value)


def json_error(message, status=400):
    return jsonify({"message": message}), status


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@student_bp.route("/dashboard", methods=["GET"])
@role_required("student")
def student_dashboard():
    student = current_student()

    bookings = Booking.query.filter_by(
        student_id=student.id
    ).all()

    active = sum(
        1 for booking in bookings
        if booking.status == ACTIVE_BOOKING
    )

    return jsonify({
        "message": "Student dashboard",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email
        },
        "total_bookings": len(bookings),
        "active_bookings": active,
        "cancelled_bookings": len(bookings) - active
    }), 200


# ==========================================
# VIEW EXAMINATIONS
# ==========================================

@student_bp.route("/examinations", methods=["GET"])
@role_required("student")
def student_examinations():
    exams = Examination.query.order_by(
        Examination.id.desc()
    ).all()

    results = []

    for exam in exams:
        results.append({
            "id": exam.id,
            "name": exam.name,
            "course_id": exam.course_id,
            "exam_type": exam.exam_type,
            "duration": exam.duration,
            "max_marks": exam.max_marks,
            "status": exam.status,
            "booking_start": (
                exam.booking_start.isoformat()
                if exam.booking_start else None
            ),
            "booking_end": (
                exam.booking_end.isoformat()
                if exam.booking_end else None
            ),
            "booking_open": exam_is_bookable(exam)
        })

    return jsonify({
        "total": len(results),
        "examinations": results
    }), 200


# ==========================================
# VIEW AVAILABLE EXAMINATION SLOTS
# ==========================================

@student_bp.route(
    "/examinations/<int:exam_id>/slots",
    methods=["GET"]
)
@role_required("student")
def available_slots(exam_id):
    exam = db.session.get(Examination, exam_id)

    if not exam:
        return json_error(
            "Examination not found", 404
        )

    slots = ExaminationSlot.query.filter_by(
        examination_id=exam_id,
        status="active"
    ).order_by(
        ExaminationSlot.start_time
    ).all()

    results = [
        slot_to_dict(slot)
        for slot in slots
        if slot_is_bookable(slot)
    ]

    return jsonify({
        "examination_id": exam_id,
        "examination_name": exam.name,
        "booking_open": exam_is_bookable(exam),
        "slots": results,
        "total": len(results)
    }), 200


# ==========================================
# CREATE BOOKING - ATOMIC SQLITE TRANSACTION
# ==========================================

@student_bp.route("/bookings", methods=["POST"])
@role_required("student")
def create_booking():
    student = current_student()
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return json_error("Valid JSON is required")

    try:
        slot_id = data.get("slot_id")

        if isinstance(slot_id, bool):
            raise ValueError()

        slot_id = int(slot_id)

        if slot_id <= 0:
            raise ValueError()

    except (TypeError, ValueError):
        return json_error("Valid slot_id is required")

    # Ensure previous ORM reads do not leave a
    # competing SQLite read transaction open.
    db.session.rollback()

    conn = sqlite_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        slot = conn.execute(
            """
            SELECT id, examination_id, examiner_id,
                   start_time, end_time,
                   capacity, status
            FROM examination_slots
            WHERE id = ?
            """,
            (slot_id,)
        ).fetchone()

        if slot is None:
            conn.rollback()
            return json_error("Slot not found", 404)

        exam = conn.execute(
            """
            SELECT id, name, status,
                   booking_start, booking_end
            FROM examinations
            WHERE id = ?
            """,
            (slot["examination_id"],)
        ).fetchone()

        if exam is None:
            conn.rollback()
            return json_error(
                "Examination not found", 404
            )

        if exam["status"].strip().lower() in CLOSED_EXAM_STATUSES:
            conn.rollback()
            return json_error(
                "Examination is not open for booking",
                409
            )

        booking_start = parse_db_datetime(
            exam["booking_start"]
        )
        booking_end = parse_db_datetime(
            exam["booking_end"]
        )

        current_utc = now_utc()

        if (
            booking_start is None
            or booking_end is None
            or not (
                booking_start <= current_utc <= booking_end
            )
        ):
            conn.rollback()
            return json_error(
                "Booking period is not currently open",
                409
            )

        start_time = parse_db_datetime(
            slot["start_time"]
        )
        end_time = parse_db_datetime(
            slot["end_time"]
        )

        if (
            slot["status"] != "active"
            or start_time <= now_utc()
        ):
            conn.rollback()
            return json_error(
                "Slot is not available", 409
            )

        if slot["capacity"] <= 0:
            conn.rollback()
            return json_error(
                "Slot has invalid capacity", 409
            )

        # Reject an existing active booking
        # for the same examination.
        duplicate = conn.execute(
            """
            SELECT b.id
            FROM bookings b
            JOIN examination_slots s
              ON s.id = b.slot_id
            WHERE b.student_id = ?
              AND b.status = ?
              AND s.examination_id = ?
            LIMIT 1
            """,
            (
                student.id,
                ACTIVE_BOOKING,
                slot["examination_id"]
            )
        ).fetchone()

        if duplicate:
            conn.rollback()
            return json_error(
                "You already booked this examination",
                409
            )

        # Prevent overlapping bookings
        # across different examinations.
        overlap = conn.execute(
            """
            SELECT b.id
            FROM bookings b
            JOIN examination_slots s
              ON s.id = b.slot_id
            WHERE b.student_id = ?
              AND b.status = ?
              AND s.start_time < ?
              AND s.end_time > ?
            LIMIT 1
            """,
            (
                student.id,
                ACTIVE_BOOKING,
                slot["end_time"],
                slot["start_time"]
            )
        ).fetchone()

        if overlap:
            conn.rollback()
            return json_error(
                "You already have an overlapping booking",
                409
            )

        booked_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM bookings
            WHERE slot_id = ?
              AND status = ?
            """,
            (slot_id, ACTIVE_BOOKING)
        ).fetchone()[0]

        if booked_count >= slot["capacity"]:
            conn.rollback()
            return json_error(
                "Slot is fully booked", 409
            )

        cursor = conn.execute(
            """
            INSERT INTO bookings
                (student_id, slot_id,
                 booking_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                student.id,
                slot_id,
                now_utc().isoformat(
                    sep=" ", timespec="microseconds"
                ),
                ACTIVE_BOOKING
            )
        )

        booking_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "message": "Slot booked successfully",
            "booking": {
                "id": booking_id,
                "student_id": student.id,
                "slot_id": slot_id,
                "examination_id": slot["examination_id"],
                "status": ACTIVE_BOOKING
            }
        }), 201

    except sqlite3.Error as e:
        conn.rollback()
        print("BOOKING DATABASE ERROR:", repr(e), flush=True)
        return json_error(
            "Database error while creating booking",
            500
        )

    finally:
        conn.close()
        db.session.expire_all()


# ==========================================
# VIEW BOOKING HISTORY
# ==========================================

@student_bp.route("/bookings", methods=["GET"])
@role_required("student")
def get_bookings():
    student = current_student()

    bookings = Booking.query.filter_by(
        student_id=student.id
    ).order_by(
        Booking.id.desc()
    ).all()

    return jsonify({
        "total": len(bookings),
        "bookings": [
            booking_to_dict(booking)
            for booking in bookings
        ]
    }), 200


# ==========================================
# VIEW SINGLE BOOKING
# ==========================================

@student_bp.route(
    "/bookings/<int:booking_id>",
    methods=["GET"]
)
@role_required("student")
def get_booking(booking_id):
    student = current_student()

    booking = Booking.query.filter_by(
        id=booking_id,
        student_id=student.id
    ).first()

    if not booking:
        return json_error("Booking not found", 404)

    return jsonify({
        "booking": booking_to_dict(booking)
    }), 200


# ==========================================
# CANCEL BOOKING
# ==========================================

@student_bp.route(
    "/bookings/<int:booking_id>/cancel",
    methods=["PATCH"]
)
@role_required("student")
def cancel_booking(booking_id):
    student = current_student()

    db.session.rollback()
    conn = sqlite_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        booking = conn.execute(
            """
            SELECT b.id, b.student_id, b.status,
                   s.start_time
            FROM bookings b
            JOIN examination_slots s
              ON s.id = b.slot_id
            WHERE b.id = ?
              AND b.student_id = ?
            """,
            (booking_id, student.id)
        ).fetchone()

        if not booking:
            conn.rollback()
            return json_error(
                "Booking not found", 404
            )

        if booking["status"] != ACTIVE_BOOKING:
            conn.rollback()
            return json_error(
                "Booking is not active", 409
            )

        slot_start = parse_db_datetime(
            booking["start_time"]
        )

        if slot_start <= now_utc():
            conn.rollback()
            return json_error(
                "Cannot cancel after slot starts",
                409
            )

        conn.execute(
            """
            UPDATE bookings
            SET status = ?
            WHERE id = ?
              AND student_id = ?
              AND status = ?
            """,
            (
                CANCELLED_BOOKING,
                booking_id,
                student.id,
                ACTIVE_BOOKING
            )
        )

        conn.commit()

        return jsonify({
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "status": CANCELLED_BOOKING
        }), 200

    except sqlite3.Error:
        conn.rollback()
        return json_error(
            "Database error while cancelling booking",
            500
        )

    finally:
        conn.close()
        db.session.expire_all()


# ============================================================
# STEP 11 - STUDENT RESULTS
# ============================================================

@student_bp.route("/results", methods=["GET"])
@role_required("student")
def get_student_results():

    student = current_student()

    evaluations = (
        Evaluation.query
        .join(
            Booking,
            Evaluation.booking_id == Booking.id
        )
        .filter(
            Booking.student_id == student.id,
            Booking.status == "booked",
            Evaluation.is_published.is_(True),
            Evaluation.status == "Finalized"
        )
        .order_by(Evaluation.id.desc())
        .all()
    )

    results = []

    for evaluation in evaluations:

        booking = db.session.get(
            Booking, evaluation.booking_id
        )

        slot = db.session.get(
            ExaminationSlot, booking.slot_id
        )

        exam = db.session.get(
            Examination, slot.examination_id
        )

        marks = (
            db.session.query(EvaluationMark, Rubric)
            .join(
                Rubric,
                EvaluationMark.rubric_id == Rubric.id
            )
            .filter(
                EvaluationMark.evaluation_id == evaluation.id
            )
            .order_by(Rubric.id)
            .all()
        )

        results.append({
            "evaluation_id": evaluation.id,
            "booking_id": booking.id,
            "examination_id": exam.id,
            "examination_name": exam.name,
            "maximum_marks": exam.max_marks,
            "total_marks": evaluation.total_marks,
            "remarks": evaluation.remarks,
            "evaluation_date": (
                evaluation.evaluation_date.isoformat()
                if evaluation.evaluation_date else None
            ),
            "rubric_marks": [
                {
                    "rubric_id": rubric.id,
                    "criterion_name": rubric.criterion_name,
                    "maximum_marks": rubric.max_marks,
                    "marks_obtained": mark.marks_obtained
                }
                for mark, rubric in marks
            ]
        })

    return jsonify({
        "student_id": student.id,
        "student_name": student.name,
        "total_results": len(results),
        "results": results
    }), 200