```python
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

app = Flask(__name__)
app.secret_key = 'sat2026_secure_key'

# ─────────────────────────────────────────────────────────────
# DATABASE CONFIG (RAILWAY)
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': os.getenv("MYSQLHOST"),
    'user': os.getenv("MYSQLUSER"),
    'password': os.getenv("MYSQLPASSWORD"),
    'database': os.getenv("MYSQLDATABASE"),
    'port': int(os.getenv("MYSQLPORT", 3306)),
    'charset': 'utf8mb4'
}

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

CENTRES = {
    'Pammal': 'pmld',
    'Pallavaram': 'pvmd',
    'Chrompet': 'chrd',
}

EXAM_DATES = [
    '29 March 2026 (Sunday)',
    '04 April 2026 (Saturday)'
]

TIMINGS = [
    '7:00 AM','7:30 AM','8:00 AM','8:30 AM',
    '9:00 AM','9:30 AM','10:00 AM','10:30 AM',
    '11:00 AM','11:30 AM','12:00 PM','12:30 PM','1:00 PM'
]

# ─────────────────────────────────────────────────────────────
# DB FUNCTIONS
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        admit_card_no VARCHAR(20) UNIQUE,
        name VARCHAR(100),
        gender ENUM('Male','Female'),
        mobile VARCHAR(15),
        exam_centre VARCHAR(30),
        exam_date VARCHAR(50),
        exam_time VARCHAR(15),
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active TINYINT(1) DEFAULT 1
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────────────────────────────
# ADMIT NUMBER START FROM 901
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
    c.drawString(50, H - 80, f"Hall Ticket: {s['admit_card_no']}")
    c.drawString(50, H - 110, f"Name: {s['name']}")
    c.drawString(50, H - 140, f"Gender: {s['gender']}")
    c.drawString(50, H - 170, f"Mobile: {s['mobile']}")
    c.drawString(50, H - 200, f"Centre: {s['exam_centre']}")
    c.drawString(50, H - 230, f"Date: {s['exam_date']}")
    c.drawString(50, H - 260, f"Time: {s['exam_time']}")

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
        name = request.form.get('name')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        centre = request.form.get('exam_centre')
        date = request.form.get('exam_date')
        time = request.form.get('exam_time')

        if not re.match(r'^\d{10}$', mobile):
            flash("Invalid mobile", "danger")
            return redirect('/register')

        admit_no = generate_admit_no(centre)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO registrations
        (admit_card_no, name, gender, mobile,
         exam_centre, exam_date, exam_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (admit_no, name, gender, mobile, centre, date, time))

        conn.commit()
        cur.close()
        conn.close()

        flash(f"Registered! Your Hall Ticket: {admit_no}", "success")
        return redirect('/check')

    return render_template('register.html',
                           centres=CENTRES,
                           timings=TIMINGS,
                           exam_dates=EXAM_DATES)


@app.route('/check', methods=['GET', 'POST'])
def check():
    students = []

    if request.method == 'POST':
        mobile = request.form.get('mobile')

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM registrations WHERE mobile=%s", (mobile,))
        students = cur.fetchall()

        cur.close()
        conn.close()

    return render_template('check.html', students=students)


@app.route('/download/<int:id>')
def download(id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM registrations WHERE id=%s", (id,))
    s = cur.fetchone()

    cur.close()
    conn.close()

    pdf = build_admit_pdf(s)

    return send_file(pdf,
                     as_attachment=True,
                     download_name=f"{s['admit_card_no']}.pdf",
                     mimetype='application/pdf')


# ─────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        flash("Invalid login", "danger")
    return render_template('admin_login.html')


@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM registrations")
    total = cur.fetchone()['total']

    cur.close()
    conn.close()

    return render_template('admin.html', total=total)


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
```
