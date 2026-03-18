"""
SAT 2026 — Setup Checker
Run this FIRST to verify your environment before starting app.py

    python check_setup.py
"""
import sys, os, subprocess

OK  = "  ✅"
ERR = "  ❌"
WARN= "  ⚠️ "

print("\n" + "="*55)
print("   CSC SAT 2026 — Environment Check")
print("="*55)

# 1. Python version
major, minor = sys.version_info[:2]
ver = f"{major}.{minor}"
if major == 3 and minor >= 8:
    print(f"{OK} Python {ver}")
else:
    print(f"{ERR} Python {ver}  — need 3.8+. Download: python.org")

# 2. Required packages
packages = {
    'flask':               'flask',
    'mysql.connector':     'mysql-connector-python',
    'openpyxl':            'openpyxl',
    'reportlab':           'reportlab',
}
missing = []
for imp, pkg in packages.items():
    try:
        __import__(imp)
        print(f"{OK} {pkg}")
    except ImportError:
        print(f"{ERR} {pkg}  — not installed")
        missing.append(pkg)

if missing:
    print(f"\n  Run this to install missing packages:")
    print(f"    pip install {' '.join(missing)}\n")

# 3. MySQL connection
print()
print("  Checking MySQL connection...")

# Read DB_CONFIG from app.py  (simple parse)
db_password = ''
db_host     = 'localhost'
db_user     = 'root'
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        for line in f:
            if "'password'" in line and ':' in line:
                # e.g.  'password': '',
                val = line.split(':', 1)[1].strip().strip(',').strip()
                val = val.strip("'\"")
                db_password = val
                break
except Exception:
    pass

try:
    import mysql.connector
    conn = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, connection_timeout=4
    )
    conn.close()
    print(f"{OK} MySQL is running and accepting connections")
    print(f"     host={db_host}  user={db_user}")
except Exception as e:
    print(f"{ERR} MySQL NOT reachable — {e}")
    print()
    print("  ─── How to start MySQL on Windows ───────────────")
    print("  Option A (XAMPP):   Open XAMPP Control Panel → click 'Start' next to MySQL")
    print("  Option B (WAMP):    Click WAMP tray icon → Start All Services")
    print("  Option C (Service): Press Win+R → services.msc → find MySQL80 → Start")
    print("  Option D (CMD as Admin):")
    print("    net start MySQL80")
    print()
    print("  If MySQL is installed but the password is wrong,")
    print("  edit app.py line with 'password': '' and put your password.")
    print("  ──────────────────────────────────────────────────")

# 4. Folder structure
print()
print("  Checking folder structure...")
required = [
    'app.py',
    'templates/base.html',
    'templates/index.html',
    'templates/register.html',
    'templates/check_admit.html',
    'templates/admin_login.html',
    'templates/admin_base.html',
    'templates/admin_dashboard.html',
    'templates/admin_students.html',
]
all_ok = True
for path in required:
    if os.path.exists(path):
        print(f"{OK} {path}")
    else:
        print(f"{ERR} MISSING: {path}")
        all_ok = False

if not all_ok:
    print()
    print("  ─── Folder structure fix ─────────────────────────")
    print("  Your project folder should look like this:")
    print()
    print("  admit card/")
    print("  ├── app.py")
    print("  ├── requirements.txt")
    print("  ├── setup_db.sql")
    print("  └── templates/")
    print("      ├── base.html")
    print("      ├── index.html")
    print("      ├── register.html")
    print("      ├── check_admit.html")
    print("      ├── admin_login.html")
    print("      ├── admin_base.html")
    print("      ├── admin_dashboard.html")
    print("      └── admin_students.html")
    print()
    print("  Make sure ALL template files are inside the 'templates' subfolder")
    print("  in the SAME directory as app.py.")
    print("  ──────────────────────────────────────────────────")

print()
print("="*55)
if missing or not all_ok:
    print("  Fix the issues above, then run:  python app.py")
else:
    print("  All checks passed!")
    print("  Run:  python app.py")
    print("  Open: http://localhost:5000")
print("="*55 + "\n")
