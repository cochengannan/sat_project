<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Admin — CSC SAT 2026{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {
      --red: #D32F2F; --red-dark: #B71C1C;
      --navy: #1A237E; --navy-light: #283593;
      --gold: #F9A825;
      --sidebar-w: 250px;
    }
    * { box-sizing: border-box; }
    body { font-family: 'Poppins', sans-serif; background: #F0F2F5; min-height: 100vh; display: flex; flex-direction: column; }

    /* ── SIDEBAR ── */
    .admin-sidebar {
      width: var(--sidebar-w);
      background: linear-gradient(180deg, var(--navy) 0%, #0d1257 100%);
      position: fixed; top: 0; left: 0; bottom: 0;
      z-index: 1050;
      display: flex; flex-direction: column;
      box-shadow: 4px 0 20px rgba(0,0,0,0.3);
      transition: transform 0.3s;
    }
    .sidebar-brand {
      padding: 20px 18px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .brand-circle {
      width: 46px; height: 46px;
      border-radius: 50%;
      background: var(--navy);
      border: 2px solid var(--gold);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      flex-shrink: 0;
    }
    .brand-circle span.csc { color: var(--gold); font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 15px; line-height: 1; }
    .brand-circle span.iso { color: #fff; font-size: 4px; line-height: 1.3; text-align: center; }
    .brand-name { color: #fff; font-weight: 700; font-size: 13px; line-height: 1.3; }
    .brand-sub { color: var(--gold); font-size: 10px; font-weight: 500; }

    .sidebar-label {
      color: rgba(255,255,255,0.35);
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 1.5px;
      padding: 14px 18px 6px;
      text-transform: uppercase;
    }
    .sidebar-nav a {
      display: flex; align-items: center; gap: 12px;
      color: rgba(255,255,255,0.65);
      text-decoration: none;
      font-size: 13px; font-weight: 500;
      padding: 10px 18px;
      border-radius: 0;
      transition: all 0.2s;
      position: relative;
    }
    .sidebar-nav a .nav-icon {
      width: 32px; height: 32px;
      border-radius: 8px;
      background: rgba(255,255,255,0.08);
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; flex-shrink: 0;
    }
    .sidebar-nav a:hover, .sidebar-nav a.active {
      color: #fff;
      background: rgba(255,255,255,0.1);
    }
    .sidebar-nav a.active .nav-icon {
      background: var(--red);
    }
    .sidebar-nav a.active::after {
      content: '';
      position: absolute; right: 0; top: 50%;
      transform: translateY(-50%);
      width: 3px; height: 60%;
      background: var(--gold);
      border-radius: 2px 0 0 2px;
    }
    .sidebar-footer {
      margin-top: auto;
      padding: 16px 18px;
      border-top: 1px solid rgba(255,255,255,0.08);
    }
    .sidebar-footer a {
      color: rgba(255,255,255,0.5);
      text-decoration: none;
      font-size: 12px;
      display: flex; align-items: center; gap: 8px;
    }
    .sidebar-footer a:hover { color: rgba(255,255,255,0.9); }

    /* ── MAIN ── */
    .admin-main {
      margin-left: var(--sidebar-w);
      flex: 1;
      display: flex; flex-direction: column;
    }
    .admin-topbar {
      background: #fff;
      padding: 12px 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 100;
    }
    .topbar-title { font-weight: 700; color: var(--navy); font-size: 16px; }
    .topbar-meta { font-size: 12px; color: #aaa; }
    .admin-badge {
      background: var(--navy);
      color: #fff;
      font-size: 11px; font-weight: 700;
      padding: 4px 12px; border-radius: 20px;
      display: flex; align-items: center; gap: 6px;
    }
    .admin-content { padding: 24px; flex: 1; }

    /* ── FLASH ── */
    .flash-area { padding: 0 0 4px; }

    /* ── STAT CARDS ── */
    .stat-card {
      background: #fff;
      border-radius: 14px;
      padding: 20px 20px 16px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
      display: flex; align-items: center; gap: 16px;
      border-left: 5px solid transparent;
      transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card .sc-icon {
      width: 50px; height: 50px;
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; flex-shrink: 0;
    }
    .stat-card .sc-num { font-size: 28px; font-weight: 800; color: var(--navy); line-height: 1; }
    .stat-card .sc-label { font-size: 12px; color: #888; margin-top: 2px; }
    .stat-card.red { border-left-color: var(--red); }
    .stat-card.red .sc-icon { background: #ffebee; color: var(--red); }
    .stat-card.navy { border-left-color: var(--navy); }
    .stat-card.navy .sc-icon { background: #e8eaf6; color: var(--navy); }
    .stat-card.gold { border-left-color: var(--gold); }
    .stat-card.gold .sc-icon { background: #fff8e1; color: #e65100; }
    .stat-card.green { border-left-color: #43a047; }
    .stat-card.green .sc-icon { background: #e8f5e9; color: #43a047; }

    /* ── TABLE ── */
    .sat-table { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
    .sat-table thead th { background: var(--navy); color: #fff; font-size: 12px; font-weight: 600; padding: 12px 14px; white-space: nowrap; }
    .sat-table tbody tr:hover { background: #f5f5ff; }
    .sat-table td { font-size: 13px; vertical-align: middle; padding: 10px 14px; }

    .badge-centre {
      background: #e8eaf6; color: var(--navy);
      font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px;
    }
    .badge-male { background: #e3f2fd; color: #1565c0; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
    .badge-female { background: #fce4ec; color: #c2185b; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }

    /* PAGE TITLE */
    .page-header { margin-bottom: 20px; }
    .page-header h4 { font-weight: 800; color: var(--navy); margin: 0; font-size: 20px; }
    .page-header p { color: #aaa; font-size: 13px; margin: 4px 0 0; }

    /* FILTER BAR */
    .filter-bar {
      background: #fff;
      border-radius: 14px;
      padding: 18px 20px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.05);
      margin-bottom: 20px;
    }

    @media (max-width: 768px) {
      .admin-sidebar { transform: translateX(-100%); }
      .admin-sidebar.open { transform: translateX(0); }
      .admin-main { margin-left: 0; }
    }
  </style>
  {% block extra_css %}{% endblock %}
</head>
<body>

<!-- SIDEBAR -->
<aside class="admin-sidebar" id="adminSidebar">
  <div class="sidebar-brand d-flex align-items-center gap-3">
    <div class="brand-circle">
      <span class="csc">CSC</span>
      <span class="iso">ISO 9001</span>
    </div>
    <div>
      <div class="brand-name">Admin Portal</div>
      <div class="brand-sub">CSC SAT 2026</div>
    </div>
  </div>

  <div class="sidebar-label">Main Menu</div>
  <nav class="sidebar-nav">
    <a href="{{ url_for('admin_dashboard') }}" class="{% if request.endpoint == 'admin_dashboard' %}active{% endif %}">
      <div class="nav-icon"><i class="fas fa-tachometer-alt"></i></div>
      Dashboard
    </a>
    <a href="{{ url_for('admin_students') }}" class="{% if request.endpoint == 'admin_students' %}active{% endif %}">
      <div class="nav-icon"><i class="fas fa-users"></i></div>
      All Registrations
    </a>
  </nav>

  <div class="sidebar-label">Exports</div>
  <nav class="sidebar-nav">
    <a href="{{ url_for('download_excel') }}">
      <div class="nav-icon"><i class="fas fa-file-excel"></i></div>
      Export Excel
    </a>
    <a href="{{ url_for('download_pdf_list') }}">
      <div class="nav-icon"><i class="fas fa-file-pdf"></i></div>
      Export PDF
    </a>
  </nav>

  <div class="sidebar-label">Public</div>
  <nav class="sidebar-nav">
    <a href="{{ url_for('index') }}" target="_blank">
      <div class="nav-icon"><i class="fas fa-external-link-alt"></i></div>
      View Website
    </a>
  </nav>

  <div class="sidebar-footer">
    <a href="{{ url_for('admin_logout') }}">
      <i class="fas fa-sign-out-alt"></i> Logout
    </a>
  </div>
</aside>

<!-- MAIN -->
<div class="admin-main">
  <div class="admin-topbar">
    <div>
      <div class="topbar-title">{% block page_title %}Dashboard{% endblock %}</div>
      <div class="topbar-meta">CSC SAT 2026 Administration</div>
    </div>
    <div class="admin-badge">
      <i class="fas fa-user-shield"></i> Administrator
    </div>
  </div>

  <div class="admin-content">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
      <div class="flash-area">
        {% for category, message in messages %}
        <div class="alert alert-{{ category }} alert-dismissible fade show rounded-3 mb-2" role="alert">
          {{ message|safe }}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
      </div>
      {% endif %}
    {% endwith %}

    {% block admin_content %}{% endblock %}
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
{% block extra_js %}{% endblock %}
</body>
</html>
