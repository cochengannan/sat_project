{% extends 'admin_base.html' %}
{% block title %}Dashboard — CSC SAT 2026 Admin{% endblock %}
{% block page_title %}Dashboard{% endblock %}

{% block extra_css %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
{% endblock %}

{% block content %}
<!-- Stat cards -->
<div class="row g-3 mb-4">
  <div class="col-sm-6 col-xl-3">
    <div class="card stat-card p-3">
      <div class="d-flex align-items-center gap-3">
        <div style="font-size:2.2rem;color:#e60000;"><i class="bi bi-people-fill"></i></div>
        <div>
          <div class="text-muted small">Total Registered</div>
          <div class="fw-bold fs-3">{{ total }}</div>
        </div>
      </div>
    </div>
  </div>
  {% for row in by_centre %}
  <div class="col-sm-6 col-xl-3">
    <div class="card stat-card p-3" style="border-color:#0a0a6e !important;">
      <div class="d-flex align-items-center gap-3">
        <div style="font-size:2.2rem;color:#0a0a6e;"><i class="bi bi-geo-alt-fill"></i></div>
        <div>
          <div class="text-muted small">{{ row.exam_centre }}</div>
          <div class="fw-bold fs-3">{{ row.cnt }}</div>
        </div>
      </div>
    </div>
  </div>
  {% endfor %}
</div>

<!-- Charts + Recent -->
<div class="row g-4">

  <!-- Gender chart -->
  <div class="col-md-4">
    <div class="card p-4 h-100">
      <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart-fill me-1 text-danger"></i>Gender Split</h6>
      <canvas id="genderChart" height="200"></canvas>
    </div>
  </div>

  <!-- Date chart -->
  <div class="col-md-4">
    <div class="card p-4 h-100">
      <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart-fill me-1 text-primary"></i>By Exam Date</h6>
      <canvas id="dateChart" height="200"></canvas>
    </div>
  </div>

  <!-- Centre chart -->
  <div class="col-md-4">
    <div class="card p-4 h-100">
      <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart-line-fill me-1 text-success"></i>By Centre</h6>
      <canvas id="centreChart" height="200"></canvas>
    </div>
  </div>

</div>

<!-- Recent registrations -->
<div class="card mt-4">
  <div class="card-header fw-bold py-3" style="background:#f8f9ff;">
    <i class="bi bi-clock-history me-2 text-primary"></i>Recent Registrations (last 10)
  </div>
  <div class="table-responsive">
    <table class="table table-hover align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th>Hall Ticket</th><th>Name</th><th>Gender</th>
          <th>Mobile</th><th>Centre</th><th>Date</th><th>Time</th><th>Admit Card</th>
        </tr>
      </thead>
      <tbody>
        {% for s in recent %}
        <tr>
          <td class="fw-bold text-danger">{{ s.admit_card_no }}</td>
          <td>{{ s.name }}</td>
          <td>
            <span class="badge {{ 'bg-primary' if s.gender=='Male' else 'bg-pink' }}"
                  style="{{ 'background:#e91e8c !important;' if s.gender=='Female' else '' }}">
              {{ s.gender }}
            </span>
          </td>
          <td>{{ s.mobile }}</td>
          <td>{{ s.exam_centre }}</td>
          <td>{{ s.exam_date }}</td>
          <td>{{ s.exam_time }}</td>
          <td>
            <a href="{{ url_for('admin_download_admit', reg_id=s.id) }}"
               class="btn btn-sm btn-outline-danger">
              <i class="bi bi-download"></i>
            </a>
          </td>
        </tr>
        {% else %}
        <tr><td colspan="8" class="text-center text-muted py-4">No registrations yet.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  <div class="card-footer text-end">
    <a href="{{ url_for('admin_students') }}" class="btn btn-sm btn-navy">
      View All Students <i class="bi bi-arrow-right ms-1"></i>
    </a>
  </div>
</div>

{% endblock %}

{% block extra_js %}
<script>
const genderData = {
  labels: [{% for r in by_gender %}"{{ r.gender }}"{% if not loop.last %},{% endif %}{% endfor %}],
  counts: [{% for r in by_gender %}{{ r.cnt }}{% if not loop.last %},{% endif %}{% endfor %}]
};
const dateData = {
  labels: [{% for r in by_date %}"{{ r.exam_date[:10] }}"{% if not loop.last %},{% endif %}{% endfor %}],
  counts: [{% for r in by_date %}{{ r.cnt }}{% if not loop.last %},{% endif %}{% endfor %}]
};
const centreData = {
  labels: [{% for r in by_centre %}"{{ r.exam_centre }}"{% if not loop.last %},{% endif %}{% endfor %}],
  counts: [{% for r in by_centre %}{{ r.cnt }}{% if not loop.last %},{% endif %}{% endfor %}]
};

new Chart(document.getElementById('genderChart'), {
  type: 'doughnut',
  data: { labels: genderData.labels,
          datasets: [{ data: genderData.counts,
                       backgroundColor: ['#1565c0','#e91e8c'], borderWidth: 0 }] },
  options: { plugins: { legend: { position: 'bottom' } } }
});
new Chart(document.getElementById('dateChart'), {
  type: 'bar',
  data: { labels: dateData.labels,
          datasets: [{ label: 'Students', data: dateData.counts,
                       backgroundColor: '#0a0a6e', borderRadius: 8 }] },
  options: { plugins: { legend: { display: false } },
             scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
});
new Chart(document.getElementById('centreChart'), {
  type: 'bar',
  data: { labels: centreData.labels,
          datasets: [{ label: 'Students', data: centreData.counts,
                       backgroundColor: '#e60000', borderRadius: 8 }] },
  options: { plugins: { legend: { display: false } },
             scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
});
</script>
<style>
.btn-navy { background:#0a0a6e; color:#fff; border:none; font-weight:600; }
.btn-navy:hover { background:#07075c; color:#fff; }
</style>
{% endblock %}
