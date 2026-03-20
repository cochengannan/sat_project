from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_file, jsonify, flash)
import mysql.connector
import os, io, re
from datetime import datetime
from functools import wraps

from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdfcanvas
import openpyxl

# ─────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sat2026_secure_key")

# ─────────────────────────────────────────────────────────────
# DATABASE CONFIG
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':               os.getenv("MYSQLHOST"),
    'user':               os.getenv("MYSQLUSER"),
    'password':           os.getenv("MYSQLPASSWORD"),
    'database':           os.getenv("MYSQLDATABASE"),
    'port':               int(os.getenv("MYSQLPORT", 3306)),
    'charset':            'utf8mb4',
    'connection_timeout': 10,
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

CENTRE_ADDRESS = {
    'Pammal':     'CSC - Pammal Branch, Pammal, Chennai - 600 075',
    'Pallavaram': 'CSC - Pallavaram Branch, Pallavaram, Chennai - 600 043',
    'Chrompet':   'CSC - Chrompet Branch, Chrompet, Chennai - 600 044',
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

with app.app_context():
    try:
        init_db()
        print("Database table ready.")
    except Exception as e:
        print(f"DB init warning (non-fatal): {e}")

# ─────────────────────────────────────────────────────────────
# ADMIT NUMBER GENERATION
# Pammal: pmld901+ | Pallavaram: pvmd901+ | Chrompet: chrd901+
# ─────────────────────────────────────────────────────────────
def generate_admit_no(centre):
    prefix = CENTRES.get(centre, 'sat')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM registrations WHERE exam_centre=%s", (centre,)
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
# PDF GENERATION — overlays data on official admit card image
# Image: 1772x827px | PDF: landscape A5 = 595.3x419.5 pts
# Boxes: x=992-1530 (7 boxes, 77px each)
# ─────────────────────────────────────────────────────────────
def build_admit_pdf(s):
    buf = io.BytesIO()
    W, H = landscape(A5)
    IMG_W, IMG_H = 1772, 827
    sx = W / IMG_W
    sy = H / IMG_H

    def pos(px, py):
        return px * sx, H - py * sy

    c = pdfcanvas.Canvas(buf, pagesize=(W, H))

    img_path = os.path.join(
        os.path.dirname(__file__), 'static', 'images', 'admit_template.jpg'
    )
    c.drawImage(img_path, 0, 0, width=W, height=H)
    c.setFillColor(colors.HexColor("#00008B"))

    # ── Admit Card No — 7 chars across 7 boxes (x=992-1530) ──
    box_start = 992
    box_w = 77
    c.setFont("Helvetica-Bold", 14)
    for i, ch in enumerate(s['admit_card_no']):
        cx = box_start + i * box_w + box_w // 2
        x, y = pos(cx, 218)
        c.drawCentredString(x, y, ch)

    # ── Gender X inside M or F box ──
    c.setFont("Helvetica-Bold", 11)
    if s['gender'] == 'Male':
        x, y = pos(648, 342)
    else:
        x, y = pos(728, 342)
    c.drawString(x, y, "X")

    # ── Time on the underline ──
    x, y = pos(975, 337)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, s['exam_time'])

    # ── Name on the underline ──
    x, y = pos(762, 440)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, s['name'].upper())

    # ── Centre Address — above calendar image ──
    address = CENTRE_ADDRESS.get(s['exam_centre'], s['exam_centre'])
    x, y = pos(820, 548)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, address)

    # ── Exam Date — below address ──
    x, y = pos(820, 572)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"Exam Date : {s['exam_date']}")

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
        try:
            name   = request.form.get('name', '').strip()
            gender = request.form.get('gender', '').strip()
            mobile = request.form.get('mobile', '').strip()
            centre = request.form.get('exam_centre', '').strip()
            date   = request.form.get('exam_date', '').strip()
            time   = request.form.get('exam_time', '').strip()

            if not all([name, gender, mobile, centre, date, time]):
                flash("All fields are required.", "danger")
                return redirect('/register')

            if not re.match(r'^\d{10}$', mobile):
                flash("Invalid mobile number. Please enter a 10-digit number.", "danger")
                return redirect('/register')

            if gender not in ('Male', 'Female'):
                flash("Please select a valid gender.", "danger")
                return redirect('/register')

            admit_no = generate_admit_no(centre)

            conn = get_db()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO registrations
                    (admit_card_no, name, gender, mobile, exam_centre, exam_date, exam_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (admit_no, name, gender, mobile, centre, date, time))
            conn.commit()
            cur.close()
            conn.close()

            flash(f"Registration successful! Your Hall Ticket No: {admit_no}", "success")
            return redirect('/check_admit')

        except mysql.connector.Error as db_err:
            flash(f"Database error: {db_err}", "danger")
            return redirect('/register')
        except Exception as e:
            flash(f"Something went wrong: {e}", "danger")
            return redirect('/register')

    return render_template('register.html',
                           centres=CENTRES,
                           timings=TIMINGS,
                           exam_dates=EXAM_DATES)

@app.route('/check_admit', methods=['GET', 'POST'])
def check():
    students = []
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        try:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM registrations WHERE mobile=%s", (mobile,))
            students = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            flash(f"Database error: {e}", "danger")
    return render_template('check_admit.html', students=students)

@app.route('/download/<int:id>')
def download(id):
    try:
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
    except Exception as e:
        flash(f"Error generating PDF: {e}", "danger")
        return redirect('/check_admit')

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
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM registrations")
        total = cur.fetchone()['total']
        cur.close()
        conn.close()
    except Exception as e:
        total = 0
        flash(f"DB error: {e}", "danger")
    return render_template('admin_dashboard.html', total=total)

@app.route('/admin/students')
@admin_required
def admin_students():
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM registrations ORDER BY registered_at DESC")
        students = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        students = []
        flash(f"DB error: {e}", "danger")
    return render_template('admin_students.html', students=students)

# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
