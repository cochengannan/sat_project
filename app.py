from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_file, jsonify, flash)
import mysql.connector
import os, io, re, tempfile
from datetime import datetime
from functools import wraps
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from PIL import Image as PILImage
from reportlab.lib.pagesizes import landscape, A5, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ─────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sat2026_csc_secret_xK9mP3nQ")

# ─────────────────────────────────────────────────────────────
# DATABASE CONFIG  (env vars set in Render; falls back to local)
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.getenv("MYSQLHOST",     "127.0.0.1"),
    'user':     os.getenv("MYSQLUSER",     "root"),
    'password': os.getenv("MYSQLPASSWORD", ""),
    'database': os.getenv("MYSQLDATABASE", "sat2026_db"),
    'port':     int(os.getenv("MYSQLPORT", 3306)),
    'charset':  'utf8mb4',
}

# ─────────────────────────────────────────────────────────────
# ADMIN CREDENTIALS
# ─────────────────────────────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sat@admin2026")

# ─────────────────────────────────────────────────────────────
# EXAM CONFIG
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
# TEMPLATE IMAGE PATH
# admit_card_template.tif must be in the project root
# ─────────────────────────────────────────────────────────────
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'admit_card_template.tif')

# ─────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create registrations table if it doesn't exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admit_card_no VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            gender ENUM('Male','Female') NOT NULL,
            mobile VARCHAR(15) NOT NULL,
            exam_centre VARCHAR(30) NOT NULL,
            exam_date VARCHAR(50) NOT NULL,
            exam_time VARCHAR(15) NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active TINYINT(1) DEFAULT 1,
            INDEX idx_mobile (mobile),
            INDEX idx_admit (admit_card_no),
            INDEX idx_centre (exam_centre)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database table ready.")


def generate_admit_no(centre):
    """
    Generate hall ticket in format: pmld901, pvmd901, chrd901
    Serial starts at 901 and increments per centre.
    e.g. 1st Pammal student  → pmld901
         2nd Pammal student  → pmld902
         1st Chrompet student→ chrd901
    """
    prefix = CENTRES.get(centre, 'sat')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM registrations WHERE exam_centre=%s", (centre,)
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    serial = 901 + count
    return f"{prefix}{serial}"


# ─────────────────────────────────────────────────────────────
# AUTO-CREATE TABLE ON STARTUP
# ─────────────────────────────────────────────────────────────
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  DB init warning: {e}")

# ─────────────────────────────────────────────────────────────
# AUTH DECORATOR
# ─────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────
# PDF ADMIT CARD — overlay on official CSC template image
#
# Template image: admit_card_template.tif  (1772 × 827 px, CMYK)
#
# Verified pixel coordinates (via colour-mask analysis):
#   Admit boxes (6 boxes):
#     centres x = [1048,1135,1222,1309,1396,1484]  y = 224
#     7th char outside last box: x = 1572,           y = 224
#   M checkbox (left=791, right=844): centre x=817,  y=355
#   F checkbox (left=906, right=959): centre x=932,  y=355
#   Time value text:  x=1169, y=355
#   Name value text:  x=845,  y=460
#   Centre value text:x=1025, y=548
#   Calendar face:    x=690-849, y=593-801, centre_x=769
#     Red top bar:    y=593-629
#     Yellow month:   y≈630-670
#     White day no:   y≈676-756
#     Red bottom bar: y=776-801
# ─────────────────────────────────────────────────────────────
def build_admit_pdf(s):
    buf = io.BytesIO()

    # Load template and convert CMYK → RGB for ReportLab
    tpl = PILImage.open(TEMPLATE_PATH).convert('RGB')
    IMG_W, IMG_H = tpl.size          # 1772 × 827

    # Landscape A5
    PDF_W, PDF_H = landscape(A5)     # ~595.28 × 419.53 pts

    # Coordinate helpers
    sx = PDF_W / IMG_W               # ~0.3359 pts/px  (x scale)
    sy = PDF_H / IMG_H               # ~0.5073 pts/px  (y scale)

    def px(x):  return x * sx
    def py(y):  return PDF_H - (y * sy) - 5   # flip + baseline nudge

    # Create canvas
    c = pdfcanvas.Canvas(buf, pagesize=(PDF_W, PDF_H))

    # Draw template as background
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    tpl.save(tmp.name, 'JPEG', quality=95)
    tmp.close()
    c.drawImage(tmp.name, 0, 0, width=PDF_W, height=PDF_H)
    os.unlink(tmp.name)

    NAVY     = colors.HexColor('#0000A0')
    RED      = colors.HexColor('#CC0000')
    NAVY_CAL = colors.HexColor('#0808A6')
    YELLOW   = colors.HexColor('#E4FF00')

    admit_no  = str(s.get('admit_card_no', ''))
    gender    = str(s.get('gender', ''))
    name      = str(s.get('name', '')).upper()
    centre    = str(s.get('exam_centre', '')).upper()
    exam_time = str(s.get('exam_time', ''))
    exam_date = str(s.get('exam_date', ''))

    # ── ADMIT CARD NUMBER ──────────────────────────────────────
    # 6 boxes in template. admit_no = 7 chars (e.g. pmld901).
    # First 6 chars fill boxes; 7th sits just outside to the right.
    BOX_CENTERS = [1048, 1135, 1222, 1309, 1396, 1484]
    BOX_Y = 224

    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 16)
    for i, bx in enumerate(BOX_CENTERS):
        if i < len(admit_no):
            c.drawCentredString(px(bx), py(BOX_Y), admit_no[i].upper())

    if len(admit_no) > 6:
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(px(1572), py(BOX_Y), admit_no[6].upper())

    # ── SEX CHECKBOXES ─────────────────────────────────────────
    # M box: left=791 right=844 → centre x=817
    # F box: left=906 right=959 → centre x=932
    # Both: top=328  bottom=382 → centre y=355
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(NAVY)
    if gender == 'Male':
        c.drawCentredString(px(817), py(355), 'X')
    elif gender == 'Female':
        c.drawCentredString(px(932), py(355), 'X')

    # ── TIME VALUE ─────────────────────────────────────────────
    # Sits on the underline at y=374; text placed at y=355, x=1169
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(NAVY)
    c.drawString(px(1169), py(355), exam_time)

    # ── NAME VALUE ─────────────────────────────────────────────
    # Underline at y=482, x=841-1628; text at x=845, y=460
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(NAVY)
    c.drawString(px(845), py(460), name)

    # ── CENTRE ADDRESS VALUE ───────────────────────────────────
    # Label ends ~x=1022; value at x=1025, y=548
    c.setFont('Helvetica-Bold', 13)
    c.setFillColor(NAVY)
    c.drawString(px(1025), py(548), ' ' + centre)

    # ── CALENDAR (dynamic — only repaint for April 4) ──────────
    # Template already shows MARCH 29 SUNDAY correctly.
    # For April 4 we repaint the entire calendar face panel.
    if 'April' in exam_date:
        FX1, FX2, FCX = 690, 849, 769   # face x-bounds and centre
        FY1, FY2      = 593, 801         # face y-bounds (top, bottom in px)

        # 1. Repaint face background with navy
        c.setFillColor(NAVY_CAL)
        c.rect(px(FX1), py(FY2),
               px(FX2) - px(FX1),
               py(FY1) - py(FY2),
               fill=1, stroke=0)

        # 2. Red top bar (y=593–629)
        c.setFillColor(RED)
        c.rect(px(FX1), py(629),
               px(FX2) - px(FX1),
               py(FY1) - py(629),
               fill=1, stroke=0)

        # 3. "EXAM DATE" label
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(px(FCX), py(618) - 3, 'EXAM DATE')

        # 4. "APRIL" in yellow
        c.setFillColor(YELLOW)
        c.setFont('Helvetica-Bold', 17)
        c.drawCentredString(px(FCX), py(660) - 5, 'APRIL')

        # 5. Day number "4" in white
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 48)
        c.drawCentredString(px(FCX), py(748) - 14, '4')

        # 6. Bottom "SATURDAY" bar (y=776–801)
        c.setFillColor(RED)
        c.rect(px(FX1 + 8), py(801),
               px(FX2 - 8) - px(FX1 + 8),
               py(776) - py(801),
               fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(px(FCX), py(791) - 3, 'SATURDAY')

    c.save()
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        gender = request.form.get('gender', '')
        mobile = request.form.get('mobile', '').strip()
        centre = request.form.get('exam_centre', '')
        date   = request.form.get('exam_date', '')
        time   = request.form.get('exam_time', '')

        errors = []
        if not name:                               errors.append('Name is required.')
        if gender not in ('Male', 'Female'):       errors.append('Please select gender.')
        if not re.match(r'^\d{10}$', mobile):      errors.append('Enter a valid 10-digit mobile number.')
        if centre not in CENTRES:                  errors.append('Please select a valid centre.')
        if date not in EXAM_DATES:                 errors.append('Please select a valid exam date.')
        if time not in TIMINGS:                    errors.append('Please select a valid time slot.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', form=request.form,
                                   centres=CENTRES, timings=TIMINGS,
                                   exam_dates=EXAM_DATES)

        try:
            admit_no = generate_admit_no(centre)
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO registrations
                    (admit_card_no, name, gender, mobile,
                     exam_centre, exam_date, exam_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (admit_no, name, gender, mobile, centre, date, time))
            conn.commit()
            cur.close()
            conn.close()
            flash(
                f'Registration successful! Your Hall Ticket No is '
                f'<strong>{admit_no}</strong>. '
                f'Use your mobile number to download your admit card.',
                'success'
            )
            return redirect(url_for('check_admit'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')

    return render_template('register.html', form={},
                           centres=CENTRES, timings=TIMINGS,
                           exam_dates=EXAM_DATES)


@app.route('/check', methods=['GET', 'POST'])
def check_admit():
    student = None
    students = []
    error = None

    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        if not mobile:
            error = 'Please enter your mobile number.'
        else:
            try:
                conn = get_db()
                cur  = conn.cursor(dictionary=True)
                cur.execute(
                    "SELECT * FROM registrations "
                    "WHERE mobile=%s AND is_active=1 "
                    "ORDER BY registered_at DESC",
                    (mobile,)
                )
                students = cur.fetchall()
                cur.close()
                conn.close()
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
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM registrations WHERE id=%s AND is_active=1",
            (reg_id,)
        )
        s = cur.fetchone()
        cur.close()
        conn.close()
        if not s:
            flash('Record not found.', 'danger')
            return redirect(url_for('check_admit'))
        buf = build_admit_pdf(s)
        return send_file(
            buf, as_attachment=True,
            download_name=f"AdmitCard_{s['admit_card_no']}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error generating admit card: {str(e)}', 'danger')
        return redirect(url_for('check_admit'))


# ─────────────────────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────────────────────
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
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM registrations WHERE is_active=1")
        total = cur.fetchone()['total']
        cur.execute("SELECT exam_centre, COUNT(*) AS cnt FROM registrations WHERE is_active=1 GROUP BY exam_centre")
        by_centre = cur.fetchall()
        cur.execute("SELECT gender, COUNT(*) AS cnt FROM registrations WHERE is_active=1 GROUP BY gender")
        by_gender = cur.fetchall()
        cur.execute("SELECT exam_date, COUNT(*) AS cnt FROM registrations WHERE is_active=1 GROUP BY exam_date")
        by_date = cur.fetchall()
        cur.execute("SELECT * FROM registrations WHERE is_active=1 ORDER BY registered_at DESC LIMIT 10")
        recent = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('admin_dashboard.html',
                               total=total, by_centre=by_centre,
                               by_gender=by_gender, by_date=by_date,
                               recent=recent)
    except Exception as e:
        flash(f'DB Error: {str(e)}', 'danger')
        return render_template('admin_dashboard.html',
                               total=0, by_centre=[], by_gender=[],
                               by_date=[], recent=[])


@app.route('/admin/students')
@admin_required
def admin_students():
    search = request.args.get('q', '').strip()
    centre = request.args.get('centre', '').strip()
    date   = request.args.get('date', '').strip()
    gender = request.args.get('gender', '').strip()
    page   = int(request.args.get('page', 1))
    per    = 20
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        where  = ['is_active=1']
        params = []
        if search:
            where.append('(name LIKE %s OR mobile LIKE %s OR admit_card_no LIKE %s)')
            params += [f'%{search}%'] * 3
        if centre:
            where.append('exam_centre=%s'); params.append(centre)
        if date:
            where.append('exam_date=%s');   params.append(date)
        if gender:
            where.append('gender=%s');      params.append(gender)
        wsql = 'WHERE ' + ' AND '.join(where)
        cur.execute(f"SELECT COUNT(*) AS cnt FROM registrations {wsql}", params)
        total_rows = cur.fetchone()['cnt']
        cur.execute(
            f"SELECT * FROM registrations {wsql} "
            f"ORDER BY registered_at DESC LIMIT %s OFFSET %s",
            params + [per, (page - 1) * per]
        )
        students = cur.fetchall()
        cur.close()
        conn.close()
        return render_template(
            'admin_students.html',
            students=students, search=search,
            centre=centre, date=date, gender=gender,
            page=page, total_pages=(total_rows + per - 1) // per,
            total_rows=total_rows,
            centres=list(CENTRES.keys()), exam_dates=EXAM_DATES
        )
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template(
            'admin_students.html',
            students=[], search='', centre='', date='', gender='',
            page=1, total_pages=1, total_rows=0,
            centres=list(CENTRES.keys()), exam_dates=EXAM_DATES
        )


@app.route('/admin/download_admit/<int:reg_id>')
@admin_required
def admin_download_admit(reg_id):
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM registrations WHERE id=%s", (reg_id,))
        s = cur.fetchone()
        cur.close()
        conn.close()
        if not s:
            flash('Not found.', 'danger')
            return redirect(url_for('admin_students'))
        buf = build_admit_pdf(s)
        return send_file(
            buf, as_attachment=True,
            download_name=f"AdmitCard_{s['admit_card_no']}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/download_excel')
@admin_required
def download_excel():
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT admit_card_no, name, gender, mobile, exam_centre, "
            "exam_date, exam_time, registered_at "
            "FROM registrations WHERE is_active=1 "
            "ORDER BY exam_centre, exam_date, exam_time"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'SAT 2026'
        thin = Side(style='thin')
        bdr  = Border(left=thin, right=thin, top=thin, bottom=thin)
        hdrs = ['Hall Ticket', 'Name', 'Gender', 'Mobile',
                'Centre', 'Date', 'Time', 'Registered']
        for col, h in enumerate(hdrs, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font      = Font(bold=True, color='FFFFFF', size=11)
            cell.fill      = PatternFill('solid', fgColor='1A237E')
            cell.alignment = Alignment(horizontal='center')
            cell.border    = bdr
        for ri, r in enumerate(rows, 2):
            vals = [r['admit_card_no'], r['name'], r['gender'], r['mobile'],
                    r['exam_centre'], r['exam_date'], r['exam_time'],
                    str(r.get('registered_at', ''))]
            for ci, v in enumerate(vals, 1):
                cell = ws.cell(row=ri, column=ci, value=v)
                cell.border = bdr
                if ri % 2 == 0:
                    cell.fill = PatternFill('solid', fgColor='E8EAF6')
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(
                max(len(str(cell.value or '')) for cell in col) + 4, 40
            )

        buf   = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        fname = f"SAT2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            buf, as_attachment=True, download_name=fname,
            mimetype='application/vnd.openxmlformats-officedocument'
                     '.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Excel export failed: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/download_pdf_list')
@admin_required
def download_pdf_list():
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT admit_card_no, name, gender, mobile, exam_centre, "
            "exam_date, exam_time, registered_at "
            "FROM registrations WHERE is_active=1 "
            "ORDER BY exam_centre, exam_date, exam_time"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=landscape(A4),
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=15*mm, bottomMargin=15*mm
        )
        title_style = ParagraphStyle(
            't', fontSize=16, fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1A237E'), spaceAfter=4
        )
        sub_style = ParagraphStyle(
            's', fontSize=9, alignment=TA_CENTER,
            textColor=colors.gray, spaceAfter=12
        )
        elems = [
            Paragraph('CSC SAT 2026 — Registration List', title_style),
            Paragraph(
                f'Generated: {datetime.now().strftime("%d %B %Y %I:%M %p")}'
                f' | Total Registrations: {len(rows)}',
                sub_style
            ),
        ]
        td = [['#', 'Hall Ticket', 'Name', 'Gender', 'Mobile',
               'Centre', 'Date', 'Time', 'Registered']]
        for i, r in enumerate(rows, 1):
            ra = r.get('registered_at', '')
            if hasattr(ra, 'strftime'):
                ra = ra.strftime('%d/%m/%Y %H:%M')
            td.append([
                str(i), r['admit_card_no'], r['name'], r['gender'],
                r['mobile'], r['exam_centre'], r['exam_date'],
                r['exam_time'], str(ra)
            ])
        t = Table(
            td, repeatRows=1,
            colWidths=[10*mm, 28*mm, 50*mm, 20*mm, 30*mm,
                       28*mm, 48*mm, 22*mm, 38*mm]
        )
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#1A237E')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1),
             [colors.white, colors.HexColor('#E8EAF6')]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#C5CAE9')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elems.append(t)
        doc.build(elems)
        buf.seek(0)
        fname = f"SAT2026_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            buf, as_attachment=True, download_name=fname,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'PDF export failed: {str(e)}', 'danger')
        return redirect(url_for('admin_students'))


@app.route('/admin/api/stats')
@admin_required
def api_stats():
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT exam_centre, COUNT(*) AS cnt "
            "FROM registrations WHERE is_active=1 GROUP BY exam_centre"
        )
        by_centre = {r['exam_centre']: r['cnt'] for r in cur.fetchall()}
        cur.execute(
            "SELECT gender, COUNT(*) AS cnt "
            "FROM registrations WHERE is_active=1 GROUP BY gender"
        )
        by_gender = {r['gender']: r['cnt'] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return jsonify({'by_centre': by_centre, 'by_gender': by_gender})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
