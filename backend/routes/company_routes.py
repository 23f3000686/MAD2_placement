from flask import Blueprint, request, jsonify
from database import db
from models import PlacementDrive, Application, User

company_bp = Blueprint("company", __name__)


# Create Placement Drive
@company_bp.route("/company/create-drive", methods=["POST"])
def create_drive():

    data = request.json

    drive = PlacementDrive(
        company_id=data["company_id"],
        job_title=data["job_title"],
        description=data["description"],
        eligibility_cgpa=data["eligibility_cgpa"],
        deadline=data["deadline"]
    )

    db.session.add(drive)
    db.session.commit()

    return jsonify({"message": "Drive created successfully"})


# Get all company drives
@company_bp.route("/company/drives", methods=["GET"])
def get_drives():

    drives = PlacementDrive.query.all()

    data = []

    for d in drives:

        applicants = Application.query.filter_by(drive_id=d.id).count()

        data.append({
            "id": d.id,
            "job_title": d.job_title,
            "description": d.description,
            "deadline": d.deadline,
            "status": d.status,
            "applicants": applicants
        })

    return jsonify(data)


# Get applications for a specific drive
@company_bp.route("/company/applications/<int:drive_id>", methods=["GET"])
def get_drive_applications(drive_id):

    apps = Application.query.filter_by(drive_id=drive_id).all()

    data = []

    for a in apps:

        student = User.query.get(a.student_id)

        data.append({
            "id": a.id,
            "student": student.name,
            "status": a.status
        })

    return jsonify(data)

@company_bp.route("/company/application/<int:id>", methods=["GET"])
def get_application(id):

    app = Application.query.get(id)

    if not app:
        return {"error": "Application not found"}, 404

    student = User.query.get(app.student_id)

    return jsonify({
        "id": app.id,
        "student": student.name,
        "status": app.status
    })

@company_bp.route("/company/review/<int:id>", methods=["POST"])
def review_application(id):

    data = request.json

    app = Application.query.get(id)

    if not app:
        return {"error": "Application not found"}, 404

    app.status = data["status"]

    db.session.commit()

    return {"message": "Application updated"}

@company_bp.route("/company/drive/complete/<int:id>", methods=["POST"])
def complete_drive(id):

    drive = PlacementDrive.query.get(id)

    if not drive:
        return {"error": "Drive not found"}, 404

    drive.status = "completed"

    db.session.commit()

    return {"message": "Drive marked as complete"}