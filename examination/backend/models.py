
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


# One table for Admin, Examiner and Student
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    department = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")


# Course details
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")


# Examination details
class Examination(db.Model):
    __tablename__ = "examinations"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(
        db.Integer, db.ForeignKey("courses.id"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(30), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)

    slot_creation_start = db.Column(db.DateTime)
    slot_creation_end = db.Column(db.DateTime)
    booking_start = db.Column(db.DateTime)
    booking_end = db.Column(db.DateTime)

    status = db.Column(db.String(30), default="Draft")

    course = db.relationship("Course", backref="examinations")


# Rubric for evaluation
class Rubric(db.Model):
    __tablename__ = "rubrics"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(
        db.Integer, db.ForeignKey("examinations.id"), nullable=False
    )
    criterion_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float)
    description = db.Column(db.Text)


# Examiner assigned to examination
class ExamAssignment(db.Model):
    __tablename__ = "exam_assignments"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(
        db.Integer, db.ForeignKey("examinations.id"), nullable=False
    )
    examiner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "examination_id", "examiner_id",
            name="unique_exam_assignment"
        ),
    )


# Slots created by examiners
class ExaminationSlot(db.Model):
    __tablename__ = "examination_slots"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(
        db.Integer, db.ForeignKey("examinations.id"), nullable=False
    )
    examiner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Available")
    meeting_link = db.Column(db.String(255))


# Student bookings
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    slot_id = db.Column(
        db.Integer, db.ForeignKey("examination_slots.id"), nullable=False
    )
    booking_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    status = db.Column(db.String(20), default="Booked")

    slot = db.relationship("ExaminationSlot", backref="bookings")
    student = db.relationship("User", backref="bookings")


# Examination evaluation
class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"),
        unique=True, nullable=False
    )
    examiner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    total_marks = db.Column(db.Float, default=0)
    remarks = db.Column(db.Text)
    evaluation_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")
    is_published = db.Column(db.Boolean, default=False)


# Marks for each rubric criterion
class EvaluationMark(db.Model):
    __tablename__ = "evaluation_marks"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False
    )
    rubric_id = db.Column(
        db.Integer, db.ForeignKey("rubrics.id"), nullable=False
    )
    marks_obtained = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "evaluation_id", "rubric_id",
            name="unique_evaluation_rubric"
        ),
    )
