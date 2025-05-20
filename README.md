# Cafe & Wifi Website

## Project Overview

**Cafe & Wifi** is a Flask-based web application designed to help users find cafes that are suitable for working remotely. Users can browse existing cafes, and authenticated users can suggest new cafes. Administrators have a dedicated dashboard to manage cafes and review user suggestions.

The project demonstrates a full-stack web application development process, including:

- User authentication
- Database interactions with SQLAlchemy
- Database migrations with Flask-Migrate
- Form handling with WTForms
- Front-end templating with Jinja2 and Bootstrap

---

## Features

### User Features

- **Browse Cafes:** View a list of available cafes on the homepage.
- **User Registration:** New users can sign up for an account.
- **User Login/Logout:** Secure authentication for registered users.
- **Suggest a Cafe:** Authenticated users can submit new cafe suggestions through a form.
- **User Dashboard:** View a list of submitted suggestions and their status (Pending, Approved, Rejected).
- **View Suggestion Details:** See the full details of submitted suggestions.

### Admin Features

- **Admin Dashboard:** Manage cafes and suggestions:
  - View all listed cafes.
  - View all cafe suggestions categorized by status.
  - View full details of any suggestion.
- **Manage Suggestions:**
  - **Approve Suggestions:** Approved suggestions are added to the main cafe list.
  - **Reject Suggestions**
- **Admin Account Creation:** CLI command (`flask create-admin`) to create admin users.
- **Protected Routes:** Only accessible to authenticated admin users.

---

## Technologies Used

### Backend

- Python 3
- Flask
- SQLAlchemy
- Flask-SQLAlchemy
- Flask-Migrate
- WTForms
- Flask-WTF
- Werkzeug

### Frontend

- HTML5
- CSS3
- Jinja2
- Bootstrap 5

### Database

- SQLite (default)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/awakra/cafe-wifi-website
cd cafe-wifi-website
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
.env\Scriptsctivate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Application

In `main.py`, set your secret key and database URI:

```python
app.config['SECRET_KEY'] = 'your-secret-key''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
```

### 5. Initialize the Database and Run Migrations

```bash
# Set FLASK_APP
# Windows (cmd)
set FLASK_APP=main.py
# Windows (PowerShell)
$env:FLASK_APP="main.py"
# macOS/Linux
export FLASK_APP=main.py

# Run migration commands
flask db init         # (only once)
flask db migrate -m "Initial database schema"
flask db upgrade
```

---

## Running the Application

Make sure the virtual environment is activated and `FLASK_APP` is set.

```bash
flask run --debug
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

## Creating an Admin User

Run the CLI command:

```bash
flask create-admin
```

Follow the prompts to create an admin account.

---

## Project Structure (Simplified)

```
cafe-wifi-website/
├── main.py                     # Main Flask application
├── models.py                   # SQLAlchemy models
├── forms.py                    # WTForms definitions
├── templates/                  # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── suggest_cafe.html
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── view_suggestion.html
│   └── add_edit_cafe.html
├── static/                     # Static files
│   ├── css/
│   │   └── styles.css
│   └── img/
│       └── logo.jpg
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Future Enhancements

- Add map integration to show cafe locations.
- Add pagination and filtering to the cafe list.
- Add email notifications on suggestion approval/rejection.
- Support for multiple databases (e.g., PostgreSQL).
