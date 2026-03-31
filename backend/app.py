from flask import Flask
from flask_cors import CORS

from database import db
from models import User

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.student_routes import student_bp
from routes.company_routes import company_bp


app = Flask(__name__)

# Enable CORS for frontend
CORS(app, origins="*")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Initialize DB
db.init_app(app)


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.register_blueprint(company_bp)


# Root route
@app.route("/")
def home():
    return {"message": "Placement Portal Backend Running"}


# Initialize database and create default admin
with app.app_context():

    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:

        admin = User(
            name="Admin",
            email="admin@portal.com",
            password="admin",
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Default Admin Created")


# Run server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)