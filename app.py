from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_file, jsonify, flash)
import mysql.connector
import os, io, re
from datetime import datetime
from functools import wraps
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Allow large TIF files
PngImagePlugin.MAX_TEXT_CHUNK = 100 * (1024 ** 2)

# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sat2026_csc_secret_xK9mP3nQ")

# ─────────────────────────────────────────────────────────────
# DB CONFIG — reads env vars (Render+Railway) or falls back local
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.getenv("MYSQLHOST",     "127.0.0.1"),
    'user':     os.getenv("MYSQLUSER",     "root"),
    'password': os.getenv("MYSQLPASSWORD", ""),
    'database': os.getenv("MYSQLDATABASE", "sat2026_db"),
    'port':     int(os.getenv("MYSQLPORT", 3306)),
    'charset':  'utf8mb4',
}

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
    '7:00 AM',  '7:30 AM',
    '8:00 AM',  '8:30 AM',
    '9:00 AM',  '9:30 AM',
    '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM',
    '12:00 PM', '12:30 PM',
    '1:00 PM',
]

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, 'static', 'images', 'admit_template.tif')

# ─────────────────────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            admit_card_no VARCHAR(20)  UNIQUE NOT NULL,
            name          VARCHAR(100) NOT NULL,
            gender        ENUM('Male','Female') NOT NULL,
            mobile        VARCHAR(15)  NOT NULL,
            exam_centre   VARCHAR(30)  NOT NULL,
            exam_date     VARCHAR(50)  NOT NULL,
            exam_time     VARCHAR(15)  NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active     TINYINT(1) DEFAULT 1,
            INDEX idx_mobile (mobile),
            INDEX idx_admit  (admit_card_no),
            INDEX idx_centre (exam_centre)
        )
    """)
    conn.commit(); cur.close(); conn.close()
    print("✅ Database table ready.")

def generate_admit_no(centre):
    prefix = CENTRES.get(centre, 'sat')
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM registrations WHERE exam_centre=%s", (centre,))
    count = cur.fetchone()[0]
    cur.close(); conn.close()
    return f"{prefix}{900 + count + 1}"

# Auto-create table on startup
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  DB init: {e}")

# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────────────
# FONT LOADER
# ─────────────────────────────────────────────────────────────
def get_font(size):
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        os.path.join(BASE_DIR, 'static', 'fonts', 'DejaVuSans-Bold.ttf'),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ─────────────────────────────────────────────────────────────
# ADMIT CARD PDF — overlay on TIF image
# ─────────────────────────────────────────────────────────────
def build_admit_pdf(s):
    """
    Opens the TIF template image and overlays student data using PIL.
    Image size: 1772 x 827 px

    Calibrated pixel positions (from pixel scanning):
      Admit No boxes  : centers x=[1048,1135,1222,1309,1396,1483], y=219
      7th char        : x=1542, y=193
      Sex tick (M)    : center (815, 325)
      Sex tick (F)    : center (905, 325)
      Time value      : x=910, y=303
      Name value      : x=840, y=455 (after "Name :" label, row y=453)
      Centre value    : x=920, y=545 (after "Centre Address :", row y=542)
    """
    buf = io.BytesIO()

    # Load template
    template = Image.open(TEMPLATE_PATH).convert('RGB')
    draw     = ImageDraw.Draw(template)
    NAVY     = (0, 0, 180)

    # Fonts
    f_box  = get_font(48)   # admit no boxes
    f_val  = get_font(46)   # field values
    f_tick = get_font(44)   # tick symbol

    admit_no = str(s.get('admit_card_no', ''))
    name     = str(s.get('name', '')).upper()
    gender   = str(s.get('gender', ''))
    time_val = str(s.get('exam_time', ''))
    centre   = str(s.get('exam_centre', '')).upper()

    # ── 1. Admit Card No — 6 chars in boxes, overflow outside ────
    box_cx = [1048, 1135, 1222, 1309, 1396, 1483]
    box_cy = 219
    for i, ch in enumerate(admit_no[:6]):
        bb = draw.textbbox((0, 0), ch.upper(), font=f_box)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw.text((box_cx[i] - tw//2, box_cy - th//2), ch.upper(),
                  fill=NAVY, font=f_box)
    # Characters beyond 6 printed right after last box
    for j, ch in enumerate(admit_no[6:]):
        draw.text((1542 + j*52, 193), ch.upper(), fill=NAVY, font=f_box)

    # ── 2. Sex — tick ✓ in correct checkbox ─────────────────────
    tick = "\u2713"
    bb   = draw.textbbox((0, 0), tick, font=f_tick)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    if gender == 'Male':
        cx, cy = 817, 354
    else:
        cx, cy = 932, 354
    draw.text((cx - tw//2, cy - th//2), tick, fill=NAVY, font=f_tick)

    # ── 3. Time value ────────────────────────────────────────────
    bb = draw.textbbox((0, 0), time_val, font=f_val)
    th = bb[3] - bb[1]
    draw.text((1172, 354 - th//2), time_val, fill=NAVY, font=f_val)

    # ── 4. Name value (after "Name :" label, row y≈453) ──────────
    bb = draw.textbbox((0, 0), name, font=f_val)
    th = bb[3] - bb[1]
    draw.text((840, 453 - th//2), name, fill=NAVY, font=f_val)

    # ── 5. Centre Address value (after label, row y≈543) ─────────
    bb = draw.textbbox((0, 0), centre, font=f_val)
    th = bb[3] - bb[1]
    draw.text((1030, 543 - th//2), centre, fill=NAVY, font=f_val)

    # ── Convert to PDF ───────────────────────────────────────────
    template.save(buf, format='PDF', resolution=150)
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name   = request.form.get('name',        '').strip()
        gender = request.form.get('gender',      '')
        mobile = request.form.get('mobile',      '').strip()
        centre = request.form.get('exam_centre', '')
        date   = request.form.get('exam_date',   '')
        time   = request.form.get('exam_time',   '')

        errors = []
        if not name:                           errors.append('Name is required.')
        if gender not in ('Male', 'Female'):   errors.append('Please select gender.')
        if not re.match(r'^\d{10}$', mobile): errors.append('Enter a valid 10-digit mobile number.')
        if centre not in CENTRES:             errors.append('Please select a valid centre.')
        if date not in EXAM_DATES:            errors.append('Please select a valid exam date.')
        if time not in TIMINGS:               errors.append('Please select a valid time slot.')

        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('register.html', form=request.form,
                                   centres=CENTRES, timings=TIMINGS,
                                   exam_dates=EXAM_DATES)
        try:
            admit_no = generate_admit_no(centre)
            conn = get_db(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO registrations
                  (admit_card_no,name,gender,mobile,exam_centre,exam_date,exam_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (admit_no, name, gender, mobile, centre, date, time))
            conn.commit(); cur.close(); conn.close()
            flash(f'Registration successful! Hall Ticket No: <strong>{admit_no}</strong>. '
                  f'Enter your mobile to download your admit card.', 'success')
            return redirect(url_for('check_admit'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')

    return render_template('register.html', form={},
                           centres=CENTRES, timings=TIMINGS,
                           exam_dates=EXAM_DATES)


@app.route('/check', methods=['GET', 'POST'])
def check_admit():
    student = None; students = []; error = None
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        if not mobile:
            error = 'Please enter your mobile number.'
        else:
            try:
                conn = get_db(); cur = conn.cursor(dictionary=True)
                cur.execute(
                    "SELECT * FROM registrations WHERE mobile=%s AND is_active=1 "
                    "ORDER BY registered_at DESC", (mobile,))
                students = cur.fetchall(); cur.close(); conn.close()
                if not students:
                    error = 'No registration found for this mobile number.'
                elif len(students) == 1:
                    student = students[0]
            except Exception as e:
                error = f'Database error: {str(e)}'
    return render_template('check_admit.html',
                           student=student, students=students, error=error)


@app.route('/download_admit/<int:reg_id>')
def download_admit(reg_id):
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM registrations WHERE id=%s AND is_active=1", (reg_id,))
        s = cur.fetchone(); cur.close(); conn.close()
        if not s:
            flash('Record not found.', 'danger')
            return redirect(url_for('check_admit'))
        buf   = build_admit_pdf(s)
        fname = f"AdmitCard_{s['admit_card_no']}.pdf"
        return send_file(buf, as_attachment=True,
                         download_name=fname, mimetype='application/pdf')
    except Exception as e:
        flash(f'Error generating admit card: {str(e)}', 'danger')
        return redirect(url_for('check_admit'))


# ═══════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if (request.form.get('username') == ADMIN_USERNAME and
                request.form.get('password') == ADMIN_PASSWORD):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM registrations")
        total = cur.fetchone()['total']
        cur.execute("SELECT exam_centre, COUNT(*) AS cnt FROM registrations GROUP BY exam_centre")
        by_centre = cur.fetchall()
        cur.execute("SELECT gender, COUNT(*) AS cnt FROM registrations GROUP BY gender")
        by_gender = cur.fetchall()
        cur.execute("SELECT exam_date, COUNT(*) AS cnt FROM registrations GROUP BY exam_date")
        by_date = cur.fetchall()
        cur.execute("SELECT * FROM registrations ORDER BY registered_at DESC LIMIT 10")
        recent = cur.fetchall(); cur.close(); conn.close()
        return render_template('admin_dashboard.html', total=total,
                               by_centre=by_centre, by_gender=by_gender,
                               by_date=by_date, recent=recent)
    except Exception as e:
        flash(f'DB Error: {str(e)}', 'danger')
        return render_template('admin_dashboard.html', total=0,
                               by_centre=[], by_gender=[], by_date=[], recent=[])


@app.route('/admin/students')
@admin_required
def admin_students():
    search = request.args.get('q',      '').strip()
    centre = request.args.get('centre', '').strip()
    date   = request.args.get('date',   '').strip()
    gender = request.args.get('gender', '').strip()
    page   = int(request.args.get('page', 1)); per = 20

    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        where = ['is_active=1']; params = []
        if search:
            where.append('(name LIKE %s OR mobile LIKE %s OR admit_card_no LIKE %s)')
            params += [f'%{search}%'] * 3
        if centre: where.append('exam_centre=%s'); params.append(centre)
        if date:   where.append('exam_date=%s');   params.append(date)
        if gender: where.append('gender=%s');      params.append(gender)
        wsql = 'WHERE ' + ' AND '.join(where)
        cur.execute(f"SELECT COUNT(*) AS cnt FROM registrations {wsql}", params)
        total_rows = cur.fetchone()['cnt']
        cur.execute(
            f"SELECT * FROM registrations {wsql} "
            f"ORDER BY registered_at DESC LIMIT %s OFFSET %s",
            params + [per, (page-1)*per])
        students = cur.fetchall(); cur.close(); conn.close()
        return render_template('admin_students.html', students=students,
                               search=search, centre=centre, date=date,
                               gender=gender, page=page,
                               total_pages=(total_rows+per-1)//per,
                               total_rows=total_rows,
                               centres=list(CENTRES.keys()),
                               exam_dates=EXAM_DATES)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin_students.html', students=[], search='',
                               centre='', date='', gender='', page=1,
                               total_pages=1, total_rows=0,
                               centres=list(CENTRES.keys()),
                               exam_dates=EXAM_DATES)


@app.route('/admin/download_admit/<int:reg_id>')
@admin_required
def admin_download_admit(reg_id):
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM registrations WHERE id=%s", (reg_id,))
        s = cur.fetchone(); cur.close(); conn.close()
        if not s:
            flash('Not found.', 'danger')
            return redirect(url_for('admin_students'))
        buf = build_admit_pdf(s)
        return send_file(buf, as_attachment=True,
                         download_name=f"AdmitCard_{s['admit_card_no']}.pdf",
                         mimetype='application/pdf')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/download_excel')
@admin_required
def download_excel():
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT admit_card_no,name,gender,mobile,exam_centre,"
            "exam_date,exam_time,registered_at FROM registrations "
            "WHERE is_active=1 ORDER BY exam_centre,exam_date,exam_time")
        rows = cur.fetchall(); cur.close(); conn.close()

        wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'SAT 2026'
        thin = Side(style='thin'); bdr = Border(left=thin,right=thin,top=thin,bottom=thin)
        hdrs = ['Hall Ticket','Name','Gender','Mobile','Centre','Date','Time','Registered']
        for col, h in enumerate(hdrs, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font=Font(bold=True,color='FFFFFF',size=11)
            cell.fill=PatternFill('solid',fgColor='1A237E')
            cell.alignment=Alignment(horizontal='center'); cell.border=bdr
        for ri, r in enumerate(rows, 2):
            vals = [r['admit_card_no'],r['name'],r['gender'],r['mobile'],
                    r['exam_centre'],r['exam_date'],r['exam_time'],
                    str(r.get('registered_at',''))]
            for ci, v in enumerate(vals, 1):
                cell = ws.cell(row=ri, column=ci, value=v); cell.border=bdr
                if ri%2==0: cell.fill=PatternFill('solid',fgColor='E8EAF6')
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(
                max(len(str(cell.value or '')) for cell in col)+4, 40)
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        fname = f"SAT2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(buf, as_attachment=True, download_name=fname,
                         mimetype='application/vnd.openxmlformats-officedocument'
                                  '.spreadsheetml.sheet')
    except Exception as e:
        flash(f'Excel export failed: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/download_pdf_list')
@admin_required
def download_pdf_list():
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT admit_card_no,name,gender,mobile,exam_centre,"
            "exam_date,exam_time,registered_at FROM registrations "
            "WHERE is_active=1 ORDER BY exam_centre,exam_date,exam_time")
        rows = cur.fetchall(); cur.close(); conn.close()

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                                leftMargin=15*mm, rightMargin=15*mm,
                                topMargin=15*mm, bottomMargin=15*mm)
        ts = ParagraphStyle('t', fontSize=16, fontName='Helvetica-Bold',
                            alignment=TA_CENTER,
                            textColor=colors.HexColor('#1A237E'), spaceAfter=4)
        ss = ParagraphStyle('s', fontSize=9, alignment=TA_CENTER,
                            textColor=colors.gray, spaceAfter=12)
        elems = [
            Paragraph('CSC SAT 2026 — Registration List', ts),
            Paragraph(f'Generated: {datetime.now().strftime("%d %B %Y %I:%M %p")}'
                      f'  |  Total: {len(rows)}', ss),
        ]
        td = [['#','Hall Ticket','Name','Gender','Mobile',
               'Centre','Date','Time','Registered']]
        for i, r in enumerate(rows, 1):
            ra = r.get('registered_at','')
            if hasattr(ra,'strftime'): ra = ra.strftime('%d/%m/%Y %H:%M')
            td.append([str(i),r['admit_card_no'],r['name'],r['gender'],
                       r['mobile'],r['exam_centre'],r['exam_date'],
                       r['exam_time'],str(ra)])
        t = Table(td, repeatRows=1,
                  colWidths=[10*mm,28*mm,50*mm,20*mm,30*mm,28*mm,48*mm,22*mm,38*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A237E')),
            ('TEXTCOLOR', (0,0),(-1,0),colors.white),
            ('FONTNAME',  (0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1),8),
            ('ALIGN',     (0,0),(-1,-1),'CENTER'),
            ('VALIGN',    (0,0),(-1,-1),'MIDDLE'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),
             [colors.white, colors.HexColor('#E8EAF6')]),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#C5CAE9')),
            ('TOPPADDING',(0,0),(-1,-1),4),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        elems.append(t); doc.build(elems); buf.seek(0)
        fname = f"SAT2026_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(buf, as_attachment=True, download_name=fname,
                         mimetype='application/pdf')
    except Exception as e:
        flash(f'PDF export failed: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/api/stats')
@admin_required
def api_stats():
    try:
        conn = get_db(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exam_centre,COUNT(*) AS cnt FROM registrations GROUP BY exam_centre")
        by_centre = {r['exam_centre']:r['cnt'] for r in cur.fetchall()}
        cur.execute("SELECT gender,COUNT(*) AS cnt FROM registrations GROUP BY gender")
        by_gender = {r['gender']:r['cnt'] for r in cur.fetchall()}
        cur.close(); conn.close()
        return jsonify({'by_centre':by_centre,'by_gender':by_gender})
    except Exception as e:
        return jsonify({'error':str(e)}), 500


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
