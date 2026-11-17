
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User
import re

auth_bp = Blueprint("auth", __name__)


# Convert a user into safe JSON data
def user_to_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "contact": user.contact,
        "status": user.status
    }


# Check whether the user is logged in
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "message": "Please login first"
            }), 401

        user = db.session.get(User, session["user_id"])

        if not user or user.status != "active":
            session.clear()
            return jsonify({
                "message": "Session invalid. Login again."
            }), 401

        return func(*args, **kwargs)

    return wrapper


# Restrict routes based on user role
def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            user = db.session.get(User, session["user_id"])

            if user.role not in allowed_roles:
                return jsonify({
                    "message": "Access denied"
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Student registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    password = data.get("password")
    contact = str(data.get("contact") or "").strip()

    if not name or not email or not isinstance(password, str):
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    if len(name) > 100 or len(email) > 120 or len(contact) > 20:
        return jsonify({
            "message": "One or more fields are too long"
        }), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({
            "message": "Invalid email address"
        }), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    # Public registration always creates a student.
    # Never accept role from registration JSON.
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role="student",
        contact=contact,
        status="active"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Student registered successfully",
        "user": user_to_dict(new_user)
    }), 201


# Login for all three roles
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    email = str(data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not isinstance(password, str):
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if user.status != "active":
        return jsonify({
            "message": "Account is inactive"
        }), 403

    session.clear()
    session["user_id"] = user.id
    session["role"] = user.role
    session.permanent = True

    return jsonify({
        "message": "Login successful",
        "user": user_to_dict(user)
    }), 200


# Get the currently logged-in user
@auth_bp.route("/me", methods=["GET"])
@login_required
def current_user():
    user = db.session.get(User, session["user_id"])

    return jsonify({
        "user": user_to_dict(user)
    }), 200


# Logout
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    }), 200
