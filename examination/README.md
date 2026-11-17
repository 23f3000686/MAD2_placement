# Examination Management Portal – V2

## Project Overview

The Examination Management Portal is a web-based application designed to manage examinations, examiner assignments, examination slots, student bookings, evaluations, and result publication.

The application supports three user roles: Admin, Examiner, and Student.

## Technology Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-CORS

**Frontend**
- Vue.js 3
- Vite
- HTML, CSS, JavaScript
- Bootstrap
- Axios
- Vue Router

## Main Features

### Admin
- View dashboard statistics
- Manage courses
- Create and manage examinations
- Configure examination rubrics
- Manage examiner accounts
- Assign examiners to examinations
- Manage examination status
- View and publish examination results

### Examiner
- View assigned examinations
- Create, update, and delete examination slots
- View students booked into slots
- Evaluate students using examination rubrics
- Save draft evaluations
- Finalize evaluations

### Student
- Register and log in
- View available examinations
- View examination slots
- Book examination slots
- Cancel eligible bookings
- View published examination results

## Project Structure

```text
examination/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── examiner.py
│   │   └── student.py
│   └── instance/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── router/
│   │   ├── services/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.9 or newer
- Node.js and npm

### 1. Install Backend Dependencies

Open PowerShell in the project directory.

```powershell
cd backend
python -m pip install -r requirements.txt
```

### 2. Start the Flask Backend

```powershell
python app.py
```

The backend runs at:

http://localhost:5000

Health-check endpoint:

http://localhost:5000/api/health

### 3. Install Frontend Dependencies

Open a second PowerShell terminal in the project directory.

```powershell
cd frontend
npm install
```

### 4. Start the Vue Frontend

```powershell
npm run dev
```

Open:

http://localhost:5173

Use `localhost` consistently for the frontend and backend to support session-based authentication.

## Default Administrator Account

For local demonstration purposes:

- Email: `admin@emp.com`
- Password: `Admin@123`

The default administrator account is created automatically when the Flask application starts, if an administrator does not already exist.

Change demonstration credentials and configure `EMP_SECRET_KEY` securely before deploying outside a local environment.

## Examination Workflow

1. Admin creates an examination.
2. Admin configures rubrics and assigns examiners.
3. Admin advances the examination to Slot Creation.
4. Examiner creates examination slots during the permitted window.
5. Admin opens booking during the configured booking period.
6. Students book available examination slots.
7. Examiner records and finalizes evaluations.
8. Admin publishes results after required evaluations are finalized.
9. Students view their published results.

## Validation and Security

- Password hashing using Werkzeug
- Role-based API access control
- Flask session authentication
- Examination schedule validation
- Examiner slot overlap prevention
- Slot capacity validation
- Booking and cancellation restrictions
- Rubric marks validation
- Finalized evaluation protection
- Result publication restrictions

## Database

SQLite is used for local data storage.

Database tables are created automatically through SQLAlchemy when the Flask application starts.

## Testing

The application has been manually tested for:

- Role-based login and dashboard navigation
- Examination and rubric configuration
- Examiner assignment
- Slot creation and overlap prevention
- Student booking and seat availability updates
- Student booking cancellation
- Evaluation draft saving and finalization
- Admin result publication
- Student access to published results

## Notes

This project is configured for local development and demonstration. Production deployment requires additional security configuration and testing.