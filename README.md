# Pet Adoption Management System

A Flask-based web application for browsing adoptable pets, submitting adoption applications, and managing adoption and volunteer requests through role-based access control.

This project was developed as a learning project and is intended for local development, not production deployment.

## Features

### Pet adopters
- Register and log in with a username and password.
- Browse available cats and dogs, filter by species, and view pet details and reviews.
- Add or remove pets from a session-based favourites list.
- Submit adoption applications for favourite pets and view application statuses.
- Delete non-completed applications and submit pet reviews.
- Apply to become a volunteer.

### Volunteers
- View adoption applications by status: `Submitted`, `Processing`, or `Completed`.
- Move submitted applications into processing.
- Finish processing an application.
- Confirm an adoption, updating the selected pet to `adopted` and the application to `Completed`.

### Administrators
- Review volunteer applications.
- Approve or reject volunteer requests.
- Grant volunteer permissions when an application is approved.
- Access volunteer adoption-management functions.

## Tech stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Jinja2 templates
- **Database:** SQLite (`sqlite3`)
- **Forms and CSRF protection:** Flask-WTF, WTForms
- **Sessions:** Flask-Session (filesystem-backed)
- **Password security:** Werkzeug password hashing

## Project structure

```text
pet-adoption/
├── app.py                 # Flask routes and application logic
├── database.py            # SQLite connection handling
├── forms.py               # WTForms form definitions
├── schema.sql             # Original database schema and seed pet data
├── migrate_roles.py       # Migration for roles and volunteer applications
├── bootstrap_admin.py     # Local utility for granting the initial admin role
├── templates/             # Jinja2 HTML templates
├── static/                # CSS and pet images
└── README.md
```

Local runtime files such as `app.db`, `flask_session/`, and `__pycache__/` should not be committed to a public repository.

## Getting started

### Prerequisites

- Python 3
- pip

### Install dependencies

Clone or download the repository, open a terminal in the project directory, and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install Flask Flask-Session Flask-WTF
```

The commands above use Windows PowerShell. On macOS/Linux, activate the environment with `source .venv/bin/activate`.

### Set up the database

**Important:** The included `schema.sql` is an older schema and does not create the `users.role` column or the `volunteer_applications` table. Do not assume it initializes the current application by itself.

For an existing local `app.db` created from the original schema, run the role migration:

```powershell
python migrate_roles.py
```

This migration requires an existing `app.db`. If you are starting from a clean clone without a database, the project still needs an updated database initialization script before setup can be completed reliably. Do not run the destructive `DROP TABLE` statements in `schema.sql` against a database containing data you want to keep.

To create the initial admin, first register a normal account in the application, then run this local utility:

```powershell
python bootstrap_admin.py
```

Enter the existing account's username and password when prompted. Run this utility only in a trusted local environment.

### Run the application

```powershell
python -m flask run
```

Open `http://127.0.0.1:5000` in your browser.

## User roles

| Role | Permissions |
| --- | --- |
| Guest | Browse available pets and pet details |
| User | Save favourites, submit and track adoption applications, write reviews, request volunteer access |
| Volunteer | Manage adoption applications in addition to user features |
| Admin | Review volunteer applications and manage adoption applications |

Role permissions are checked on the server using the `users.role` field.

## Adoption workflow

```text
User browses pets
      ↓
Adds pets to favourites
      ↓
Submits an adoption application
      ↓
Submitted
      ↓ Volunteer accepts visit
Processing
      ├── Finish → Completed
      └── Confirm Adoption → Completed
                              + pet marked adopted
```

`Confirm Adoption` is handled by a POST request with CSRF protection. The handler verifies that the application is in `Processing` and that the pet is still available before updating the database.

## Volunteer workflow

```text
User submits volunteer application
      ↓
Pending
      ↓ Admin reviews
Approved / Rejected
      ↓ If approved
User receives volunteer role
```

## Known limitations and planned improvements

This is an educational project with several areas for further development:

- Move the hardcoded Flask `SECRET_KEY` into an environment variable before deployment.
- Convert remaining state-changing GET routes (such as accepting visits, finishing applications, changing favourites, and deleting applications) to POST with CSRF protection.
- Add a safe, reproducible database initialization process and keep `schema.sql` consistent with migrations.
- Enable SQLite foreign-key enforcement and add database constraints where appropriate.
- Handle missing pets and empty favourites gracefully, and validate application input and state transitions more thoroughly.
- Improve handling of competing adoption applications for the same pet.
- Add automated tests for authentication, role permissions, and adoption workflows.
- Add JSON API endpoints for pet listings and pet details as an introduction to REST APIs.
- Prepare a dependency lockfile or `requirements.txt` and production deployment configuration.

