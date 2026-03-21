# CSC SAT 2026 — Web Application

A complete registration and admit card generation system for the Computer Software College Scholarship Aptitude Test 2026.

## Features
- **Public Registration Form** — students register with personal, academic & exam details
- **Admit Card Download** — enter mobile number → view & download PDF admit card
- **Admin Portal** — secure login, view all registrations, filter/search, export to Excel & PDF

---

## Tech Stack
- **Backend:** Python 3.10+ / Flask
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JS
- **Database:** MySQL 8+
- **PDF Generation:** ReportLab
- **Excel Export:** openpyxl

---

## Setup Instructions

### 1. Install Python dependencies
```bash
cd sat_project
pip install -r requirements.txt
```

### 2. Configure MySQL
Edit `app.py` — find `DB_CONFIG` and update:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'sat2026_db'
}
```

### 3. Create the database
Option A — let the app create it automatically:
```bash
python app.py
```
The app calls `init_db()` on startup.

Option B — run the SQL script manually in MySQL:
```sql
source setup_db.sql;
```

### 4. Run the application
```bash
python app.py
```
App starts at: **http://localhost:5000**

---

## URL Reference

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/register` | Student registration form |
| `/check` | Enter mobile → view & download admit card |
| `/download_admit/<id>` | Download PDF admit card |
| `/admin/login` | Admin login |
| `/admin` | Admin dashboard |
| `/admin/students` | View all students with filters |
| `/admin/download_excel` | Export all data as Excel |
| `/admin/download_pdf_list` | Export list as PDF |
| `/admin/logout` | Logout |

---

## Admin Credentials
```
Username: admin
Password: sat@admin2026
```
> **Change these in `app.py`** before deploying to production.

---

## Google Sheets Integration (Optional)
To pull data from a Google Sheets form:
1. Enable Google Sheets API in Google Cloud Console
2. Download service account key as `credentials.json`
3. Install: `pip install gspread oauth2client`
4. Use `gspread` to read rows and insert into MySQL

---

## Production Deployment
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Use **Nginx** as a reverse proxy in front of Gunicorn.
Set `app.secret_key` to a long random string for production.

---

## File Structure
```
sat_project/
├── app.py                  ← Main Flask application
├── requirements.txt        ← Python dependencies
├── setup_db.sql            ← Database setup SQL
├── templates/
│   ├── base.html           ← Public base layout
│   ├── index.html          ← Home page
│   ├── register.html       ← Registration form
│   ├── check_admit.html    ← Admit card check
│   ├── admin_base.html     ← Admin sidebar layout
│   ├── admin_login.html    ← Admin login
│   ├── admin_dashboard.html← Admin dashboard
│   └── admin_students.html ← Student list with filters
└── static/
    ├── css/                ← Custom CSS (optional)
    └── js/                 ← Custom JS (optional)
```
