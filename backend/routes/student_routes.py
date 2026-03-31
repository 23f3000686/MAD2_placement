from flask import Blueprint, jsonify
from models import Company, PlacementDrive, Application
from database import db
from models import Company
student_bp = Blueprint("student", __name__)


# Get all approved companies
@student_bp.route("/student/companies")
def get_companies():

    companies = Company.query.filter_by(approved=True).all()

    data = []

    for c in companies:
        data.append({
            "id": c.id,
            "name": c.company_name
        })

    return jsonify(data)



# Get drives applied by student
@student_bp.route("/student/applications")
def get_applications():

    apps = Application.query.all()

    data = []

    for a in apps:

        drive = PlacementDrive.query.get(a.drive_id)

        company = Company.query.get(drive.company_id)
        data.append({
            "id": a.id,
            "title": drive.job_title,
            "company": company.company_name,
            "date": drive.deadline
        })

    return jsonify(data)

@student_bp.route("/student/drive/<int:id>")
def drive_details(id):

    drive = PlacementDrive.query.get(id)

    return jsonify({
        "id": drive.id,
        "job_title": drive.job_title,
        "description": drive.description,
        "eligibility_cgpa": drive.eligibility_cgpa,
        "deadline": drive.deadline
    })

# Apply for drive
@student_bp.route("/student/apply/<int:drive_id>", methods=["POST"])
def apply_drive(drive_id):

    app = Application(
        student_id=1,
        drive_id=drive_id,
        status="Applied"
    )

    db.session.add(app)
    db.session.commit()

    return {"message":"Applied successfully"}