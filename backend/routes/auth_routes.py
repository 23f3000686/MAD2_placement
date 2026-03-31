from flask import Blueprint, request, jsonify
from models import User, Student, Company
from database import db

auth_bp = Blueprint("auth", __name__)


# Login
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    user = User.query.filter_by(
        email=data["email"],
        password=data["password"]
    ).first()

    if not user:
        return {"message": "Invalid credentials"}, 401

    return {
        "role": user.role,
        "user_id": user.id
    }


# Register Student
@auth_bp.route("/register/student", methods=["POST"])
def register_student():

    data = request.json

    existing = User.query.filter_by(email=data["email"]).first()

    if existing:
        return {"message": "Email already registered"}, 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    student = Student(
        user_id=user.id,
        branch=data["branch"],
        cgpa=data["cgpa"],
        year=data["year"]
    )

    db.session.add(student)
    db.session.commit()

    return {"message": "Student registered successfully"}

@auth_bp.route("/register/company", methods=["POST"])
def register_company():

    data = request.json

    existing_user = User.query.filter_by(email=data["email"]).first()

    if existing_user:
        return {"message": "Email already registered"}, 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role="company"
    )

    db.session.add(user)
    db.session.commit()

    company = Company(
        user_id=user.id,
        company_name=data["company_name"],
        approved=False
    )

    db.session.add(company)
    db.session.commit()

    return {"message": "Company registered"}
