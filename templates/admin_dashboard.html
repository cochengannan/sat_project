{% extends "admin_base.html" %}
{% block title %}Dashboard — Admin SAT 2026{% endblock %}
{% block content %}
<div class="d-flex align-items-center justify-content-between mb-4">
  <h3 class="fw-bold mb-0" style="color:#1B5E20;"><i class="fas fa-chart-bar me-2"></i>Dashboard</h3>
  <span class="text-muted small"><i class="fas fa-sync me-1"></i>Live Data</span>
</div>

<!-- Stats Cards -->
<div class="row g-3 mb-4">
  <div class="col-sm-6 col-lg-3">
    <div class="stat-card text-center">
      <div class="stat-icon mx-auto mb-2" style="background:#E8F5E9;"><i class="fas fa-users fa-lg" style="color:#1B5E20;"></i></div>
      <div class="stat-value">{{ total }}</div>
      <div class="stat-label">Total Registrations</div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="stat-card text-center">
      <div class="stat-icon mx-auto mb-2" style="background:#E3F2FD;"><i class="fas fa-male fa-lg" style="color:#1565C0;"></i></div>
      <div class="stat-value" style="color:#1565C0;">{{ male }}</div>
      <div class="stat-label">Male</div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="stat-card text-center">
      <div class="stat-icon mx-auto mb-2" style="background:#FCE4EC;"><i class="fas fa-female fa-lg" style="color:#c2185b;"></i></div>
      <div class="stat-value" style="color:#c2185b;">{{ female }}</div>
      <div class="stat-label">Female</div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="stat-card text-center">
      <div class="stat-icon mx-auto mb-2" style="background:#FFF8E1;"><i class="fas fa-calendar-check fa-lg" style="color:#F57F17;"></i></div>
      <div class="stat-value" style="color:#F57F17;">4 Apr</div>
      <div class="stat-label">Exam Date</div>
    </div>
  </div>
</div>

<div class="row g-4 mb-4">
  <!-- By Timing -->
  <div class="col-lg-6">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-bold" style="color:#1B5E20;border-bottom:2px solid #E8F5E9;">
        <i class="fas fa-clock me-2"></i>Registrations by Timing
      </div>
      <div class="card-body">
        <canvas id="timeChart" height="200"></canvas>
      </div>
    </div>
  </div>
  <!-- Top Centres -->
  <div class="col-lg-6">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-bold" style="color:#1B5E20;border-bottom:2px solid #E8F5E9;">
        <i class="fas fa-map-marker-alt me-2"></i>Top Exam Centres
      </div>
      <div class="card-body">
        {% if by_centre %}
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-success"><tr><th>Centre</th><th class="text-end">Count</th></tr></thead>
            <tbody>
              {% for c in by_centre %}
              <tr>
                <td>{{ c.exam_centre or '—' }}</td>
                <td class="text-end fw-bold">{{ c.cnt }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
        <p class="text-muted text-center py-3">No data yet</p>
        {% endif %}
      </div>
    </div>
  </div>
</div>

<!-- Recent Registrations -->
<div class="card border-0 shadow-sm">
  <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center" style="color:#1B5E20;border-bottom:2px solid #E8F5E9;">
    <span><i class="fas fa-list me-2"></i>Recent Registrations</span>
    <a href="/admin/students" class="btn btn-sm btn-outline-success">View All →</a>
  </div>
  <div class="card-body p-0">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-success">
          <tr><th>Admit No</th><th>Name</th><th>Mobile</th><th>Centre</th><th>Time</th><th>Registered</th></tr>
        </thead>
        <tbody>
          {% for s in recent %}
          <tr>
            <td><span class="badge" style="background:#1B5E20;">{{ s.admit_card_no }}</span></td>
            <td>{{ s.name }}</td>
            <td>{{ s.mobile }}</td>
            <td>{{ s.exam_centre or '—' }}</td>
            <td><span class="badge bg-warning text-dark">{{ s.exam_time }}</span></td>
            <td class="text-muted small">{{ s.registered_at.strftime('%d %b %Y %H:%M') if s.registered_at else '—' }}</td>
          </tr>
          {% else %}
          <tr><td colspan="6" class="text-center text-muted py-3">No registrations yet.</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}
{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
fetch('/admin/api/stats').then(r=>r.json()).then(data => {
  const timeData = data.by_time || {};
  const labels = Object.keys(timeData);
  const values = Object.values(timeData);
  new Chart(document.getElementById('timeChart'), {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['8 AM','10 AM','12 PM','2 PM'],
      datasets: [{
        label: 'Registrations',
        data: values.length ? values : [0,0,0,0],
        backgroundColor: ['#1B5E20','#2E7D32','#388E3C','#43A047'],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true, plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
    }
  });
});
</script>
{% endblock %}
