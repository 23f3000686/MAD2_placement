from flask import Blueprint, jsonify
from models import User, Company, PlacementDrive, Application
from database import db

admin_bp = Blueprint("admin", __name__)


# Dashboard stats
@admin_bp.route("/admin/stats")
def stats():

    students = User.query.filter_by(role="student").count()
    companies = Company.query.count()
    drives = PlacementDrive.query.count()

    return jsonify({
        "students": students,
        "companies": companies,
        "drives": drives
    })


# Get companies
@admin_bp.route("/admin/companies")
def get_companies():

    companies = Company.query.all()

    data = []

    for c in companies:

        data.append({
            "id": c.id,
            "name": c.company_name,
            "status": c.approved
        })

    return jsonify(data)


# Approve company
@admin_bp.route("/admin/company/approve/<int:id>", methods=["POST"])
def approve_company(id):

    company = Company.query.get(id)

    company.approved = True

    db.session.commit()

    return {"message": "Company approved"}


# Get drives
@admin_bp.route("/admin/drives")
def get_drives():

    drives = PlacementDrive.query.all()

    data = []

    for d in drives:
        data.append({
            "id": d.id,
            "name": d.job_title,
            "status": d.status
        })

    return jsonify(data)


# Mark drive completed
@admin_bp.route("/admin/drive/complete/<int:id>", methods=["POST"])
def complete_drive(id):

    drive = PlacementDrive.query.get(id)

    drive.status = "completed"

    db.session.commit()

    return {"message": "Drive marked as complete"}


# Student applications
@admin_bp.route("/admin/applications")
def get_applications():

    apps = Application.query.all()

    data = []

    for a in apps:

        student = User.query.get(a.student_id)
        drive = PlacementDrive.query.get(a.drive_id)
        company = Company.query.get(drive.company_id)

        data.append({
            "id": a.id,
            "student": student.name,
            "drive": drive.job_title,
            "company": company.company_name
        })

    return jsonify(data)