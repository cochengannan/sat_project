import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sat2026_secret_change_in_prod_abc123xyz')

    # ── MySQL ──────────────────────────────────────────────
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')        # ← set your password here
    DB_NAME     = os.environ.get('DB_NAME', 'sat2026_db')

    # ── Admin credentials ─────────────────────────────────
    ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', 'sat@admin2026')

    # ── Exam details ──────────────────────────────────────
    EXAM_DATE   = '04 April 2026'
    EXAM_DAY    = 'Saturday'
    EXAM_TIMINGS = ['8 AM', '10 AM', '12 PM', '2 PM']
    ADMIT_NO_START = 8000          # First admit card = 8001

    # ── Google Sheets (optional) ──────────────────────────
    # Set GOOGLE_SHEET_ID to enable sync from a linked Google Form sheet
    # Sheet must share view access with the service account email
    GOOGLE_SHEET_ID          = os.environ.get('GOOGLE_SHEET_ID', '')
    GOOGLE_CREDENTIALS_FILE  = os.environ.get('GOOGLE_CREDS', 'credentials.json')

    # Column mapping: sheet column index (0-based) → db field
    # Adjust these to match your Google Form field order
    SHEET_COLUMN_MAP = {
        0:  'timestamp',        # col A - Timestamp (ignored)
        1:  'name',             # col B
        2:  'gender',           # col C
        3:  'dob',              # col D  (DD/MM/YYYY)
        4:  'qualification',    # col E
        5:  'school_college',   # col F
        6:  'mobile',           # col G
        7:  'email',            # col H
        8:  'address',          # col I
        9:  'district',         # col J
        10: 'area',             # col K
        11: 'exam_centre',      # col L
        12: 'exam_time',        # col M
    }
