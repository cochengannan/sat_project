{% extends 'admin_base.html' %}
{% block title %}Students - CSC SAT 2026 Admin{% endblock %}
{% block page_title %}All Students{% endblock %}

{% block content %}

<!-- Filter bar -->
<div class="card mb-4">
  <div class="card-body py-3">
    <form method="GET" action="{{ url_for('admin_students') }}" class="row g-2 align-items-end">
      <div class="col-sm-3">
        <label class="form-label small fw-semibold mb-1">Search</label>
        <input type="text" name="q" class="form-control form-control-sm"
               placeholder="Name / Mobile / Hall Ticket" value="{{ search }}">
      </div>
      <div class="col-sm-2">
        <label class="form-label small fw-semibold mb-1">Centre</label>
        <select name="centre" class="form-select form-select-sm">
          <option value="">All</option>
          {% for c in centres %}
            <option value="{{ c }}" {{ 'selected' if centre==c else '' }}>{{ c }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-sm-3">
        <label class="form-label small fw-semibold mb-1">Date</label>
        <select name="date" class="form-select form-select-sm">
          <option value="">All</option>
          {% for d in exam_dates %}
            <option value="{{ d }}" {{ 'selected' if date==d else '' }}>{{ d }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-sm-2">
        <label class="form-label small fw-semibold mb-1">Gender</label>
        <select name="gender" class="form-select form-select-sm">
          <option value="">All</option>
          <option value="Male"   {{ 'selected' if gender=='Male'   else '' }}>Male</option>
          <option value="Female" {{ 'selected' if gender=='Female' else '' }}>Female</option>
        </select>
      </div>
      <div class="col-sm-2 d-flex gap-2">
        <button type="submit" class="btn btn-sm btn-primary flex-fill">
          <i class="bi bi-funnel"></i> Filter
        </button>
        <a href="{{ url_for('admin_students') }}" class="btn btn-sm btn-outline-secondary">
          <i class="bi bi-x"></i>
        </a>
      </div>
    </form>
  </div>
</div>

<!-- Export buttons + count -->
<div class="d-flex justify-content-between align-items-center mb-3">
  <span class="text-muted small">
    Showing <strong>{{ students|length }}</strong> of <strong>{{ total_rows }}</strong> results
  </span>
  <div class="d-flex gap-2">
    <a href="{{ url_for('download_excel') }}" class="btn btn-sm btn-success">
      <i class="bi bi-file-earmark-excel me-1"></i>Excel
    </a>
    <a href="{{ url_for('download_pdf_list') }}" class="btn btn-sm btn-danger">
      <i class="bi bi-file-earmark-pdf me-1"></i>PDF List
    </a>
  </div>
</div>

<!-- Table -->
<div class="card">
  <div class="table-responsive">
    <table class="table table-hover align-middle mb-0">
      <thead style="background:#0a0a6e; color:#fff;">
        <tr>
          <th>#</th>
          <th>Hall Ticket</th>
          <th>Name</th>
          <th>Gender</th>
          <th>Mobile</th>
          <th>Centre</th>
          <th>Exam Date</th>
          <th>Time</th>
          <th>Registered At</th>
          <th>Admit Card</th>
        </tr>
      </thead>
      <tbody>
        {% set offset = (page - 1) * 20 %}
        {% for s in students %}
        <tr>
          <td class="text-muted small">{{ offset + loop.index }}</td>
          <td class="fw-bold text-danger">{{ s.admit_card_no }}</td>
          <td>{{ s.name }}</td>
          <td>
            <span class="badge {{ 'bg-primary' if s.gender=='Male' else '' }}"
                  style="{{ 'background:#e91e8c !important;' if s.gender=='Female' else '' }}">
              {{ s.gender }}
            </span>
          </td>
          <td>{{ s.mobile }}</td>
          <td>{{ s.exam_centre }}</td>
          <td><small>{{ s.exam_date }}</small></td>
          <td>{{ s.exam_time }}</td>
          <td class="text-muted small">
            {% if s.registered_at %}
              {{ s.registered_at.strftime('%d/%m/%Y %H:%M') }}
            {% endif %}
          </td>
          <td>
            <a href="{{ url_for('admin_download_admit', reg_id=s.id) }}"
               class="btn btn-sm btn-outline-danger" title="Download Admit Card">
              <i class="bi bi-download"></i>
            </a>
          </td>
        </tr>
        {% else %}
        <tr>
          <td colspan="10" class="text-center text-muted py-5">
            <i class="bi bi-search" style="font-size:2rem;"></i>
            <p class="mt-2">No students found matching your filters.</p>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  {% if total_pages > 1 %}
  <div class="card-footer">
    <nav>
      <ul class="pagination pagination-sm justify-content-center mb-0">
        {% if page > 1 %}
          <li class="page-item">
            <a class="page-link" href="?q={{ search }}&centre={{ centre }}&date={{ date }}&gender={{ gender }}&page={{ page-1 }}">
              &laquo; Prev
            </a>
          </li>
        {% endif %}
        {% for p in range(1, total_pages+1) %}
          <li class="page-item {{ 'active' if p==page else '' }}">
            <a class="page-link" href="?q={{ search }}&centre={{ centre }}&date={{ date }}&gender={{ gender }}&page={{ p }}">
              {{ p }}
            </a>
          </li>
        {% endfor %}
        {% if page < total_pages %}
          <li class="page-item">
            <a class="page-link" href="?q={{ search }}&centre={{ centre }}&date={{ date }}&gender={{ gender }}&page={{ page+1 }}">
              Next &raquo;
            </a>
          </li>
        {% endif %}
      </ul>
    </nav>
  </div>
  {% endif %}

</div>
{% endblock %}
