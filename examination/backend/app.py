
import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from models import db, User

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.examiner import examiner_bp
from routes.student import student_bp


app = Flask(__name__)

# Flask configuration
app.config["SECRET_KEY"] = os.environ.get(
    "EMP_SECRET_KEY",
    "local-development-secret-change-before-submission"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emp.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Session configuration
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Local HTTP only
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# Same-origin frontend is preferred.
# Configure specific CORS origins later if necessary.
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173"
])

db.init_app(app)

# Register route blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(examiner_bp, url_prefix="/api/examiner")
app.register_blueprint(student_bp, url_prefix="/api/student")


@app.route("/")
def home():
    return jsonify({
        "message": "Examination Management Portal",
        "status": "running"
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# Create database tables and default Admin
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:
        admin = User(
            name="Administrator",
            email="admin@emp.com",
            password=generate_password_hash("Admin@123"),
            role="admin",
            status="active"
        )

        db.session.add(admin)
        db.session.commit()

        print("Default Admin created successfully!")

    print("Database ready!")


if __name__ == "__main__":
    app.run(debug=True)
