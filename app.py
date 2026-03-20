from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_file, jsonify, flash)
import mysql.connector
import os, io, re
from datetime import datetime
from functools import wraps

# PDF + Excel
import openpyxl
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas

# ─────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sat2026_secure_key")

# ─────────────────────────────────────────────────────────────
# DATABASE CONFIG (RAILWAY)
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.getenv("MYSQLHOST"),
    'user':     os.getenv("MYSQLUSER"),
    'password': os.getenv("MYSQLPASSWORD"),
    'database': os.getenv("MYSQLDATABASE"),
    'port':     int(os.getenv("MYSQLPORT", 3306)),
    'charset':  'utf8mb4',
}

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sat@admin2026")

CENTRES = {
    'Pammal':     'pmld',
    'Pallavaram': 'pvmd',
    'Chrompet':   'chrd',
}

EXAM_DATES = [
    '29 March 2026 (Sunday)',
    '04 April 2026 (Saturday)',
]

TIMINGS = [
    '7:00 AM', '7:30 AM',
    '8:00 AM', '8:30 AM',
    '9:00 AM', '9:30 AM',
    '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM',
    '12:00 PM', '12:30 PM',
    '1:00 PM',
]

# ─────────────────────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            admit_card_no VARCHAR(20) UNIQUE,
            name          VARCHAR(100),
            gender        ENUM('Male','Female'),
            mobile        VARCHAR(15),
            exam_centre   VARCHAR(30),
            exam_date     VARCHAR(50),
            exam_time     VARCHAR(15),
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active     TINYINT(1) DEFAULT 1
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────────────────────────────
# AUTO CREATE TABLE ON STARTUP
# ─────────────────────────────────────────────────────────────
with app.app_context():
    try:
        init_db()
        print("Database table ready.")
    except Exception as e:
        print(f"DB init warning: {e}")


# ─────────────────────────────────────────────────────────────
# ADMIT NUMBER GENERATION (starts from 901)
# ─────────────────────────────────────────────────────────────
def generate_admit_no(centre):
    prefix = CENTRES.get(centre, 'sat')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM registrations WHERE exam_centre=%s",
        (centre,)
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"{prefix}{901 + count}"


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────────────────────
def build_admit_pdf(s):
    buf = io.BytesIO()
    W, H = landscape(A5)
    c = pdfcanvas.Canvas(buf, pagesize=(W, H))

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, H - 40, "CSC SAT 2026 - ADMIT CARD")

    c.setFont("Helvetica", 12)
    c.drawString(50, H - 80,  f"Hall Ticket : {s['admit_card_no']}")
    c.drawString(50, H - 110, f"Name        : {s['name']}")
    c.drawString(50, H - 140, f"Gender      : {s['gender']}")
    c.drawString(50, H - 170, f"Mobile      : {s['mobile']}")
    c.drawString(50, H - 200, f"Centre      : {s['exam_centre']}")
    c.drawString(50, H - 230, f"Date        : {s['exam_date']}")
    c.drawString(50, H - 260, f"Time        : {s['exam_time']}")

    c.save()
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        gender = request.form.get('gender')
        mobile = request.form.get('mobile', '').strip()
        centre = request.form.get('exam_centre')
        date   = request.form.get('exam_date')
        time   = request.form.get('exam_time')

        if not re.match(r'^\d{10}$', mobile):
            flash("Invalid mobile number. Please enter a 10-digit number.", "danger")
            return redirect('/register')

        admit_no = generate_admit_no(centre)

        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO registrations
                (admit_card_no, name, gender, mobile, exam_centre, exam_date, exam_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (admit_no, name, gender, mobile, centre, date, time))
        conn.commit()
        cur.close()
        conn.close()

        flash(f"Registration successful! Your Hall Ticket No: {admit_no}", "success")
        return redirect('/check_admit')

    return render_template('register.html',
                           centres=CENTRES,
                           timings=TIMINGS,
                           exam_dates=EXAM_DATES)


@app.route('/check_admit', methods=['GET', 'POST'])
def check():
    students = []
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM registrations WHERE mobile=%s", (mobile,))
        students = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('check_admit.html', students=students)


@app.route('/download/<int:id>')
def download(id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM registrations WHERE id=%s", (id,))
    s = cur.fetchone()
    cur.close()
    conn.close()

    if not s:
        flash("Record not found.", "danger")
        return redirect('/check_admit')

    pdf = build_admit_pdf(s)
    return send_file(pdf,
                     as_attachment=True,
                     download_name=f"{s['admit_card_no']}.pdf",
                     mimetype='application/pdf')


# ─────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        flash("Invalid username or password.", "danger")
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')


@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM registrations")
    total = cur.fetchone()['total']
    cur.close()
    conn.close()
    return render_template('admin_dashboard.html', total=total)


@app.route('/admin/students')
@admin_required
def admin_students():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM registrations ORDER BY registered_at DESC")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_students.html', students=students)


# ─────────────────────────────────────────────────────────────
# RUN (local dev only - Gunicorn handles production)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
