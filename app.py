{% extends 'base.html' %}
{% block title %}Register — CSC SAT 2026{% endblock %}

{% block extra_css %}
<style>
  .reg-form-card {
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.1);
    overflow: hidden;
  }
  .reg-form-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
    color: #fff;
    padding: 22px 28px;
    display: flex; align-items: center; gap: 14px;
  }
  .reg-form-header .fh-icon {
    width: 46px; height: 46px;
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
  }
  .reg-form-header h3 { font-weight: 800; font-size: 18px; margin: 0; }
  .reg-form-header p { margin: 2px 0 0; font-size: 12px; opacity: 0.75; }
  .reg-form-body { padding: 32px 28px; }

  .section-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 24px 0 16px;
  }
  .section-divider .sd-label {
    background: var(--red);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    white-space: nowrap;
    letter-spacing: 0.5px;
  }
  .section-divider hr { flex: 1; border-color: #e0e0e0; margin: 0; }

  .gender-group { display: flex; gap: 14px; }
  .gender-option {
    flex: 1;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px 16px;
    cursor: pointer;
    display: flex; align-items: center; gap: 10px;
    transition: all 0.2s;
    font-weight: 600; color: #666;
  }
  .gender-option:has(input:checked) {
    border-color: var(--red);
    background: #fff5f5;
    color: var(--red);
  }
  .gender-option input[type=radio] { accent-color: var(--red); transform: scale(1.2); }
  .gender-option i { font-size: 18px; }

  .time-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .time-option {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px 6px;
    cursor: pointer;
    text-align: center;
    font-size: 12.5px;
    font-weight: 600;
    color: #555;
    transition: all 0.2s;
    position: relative;
  }
  .time-option:has(input:checked) {
    border-color: var(--navy);
    background: var(--navy);
    color: #fff;
  }
  .time-option input[type=radio] { position: absolute; opacity: 0; }

  .submit-row {
    background: var(--cream);
    border-top: 1px solid #e8e8e8;
    padding: 22px 28px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;
  }
  .submit-row .sr-info { font-size: 12px; color: #666; }
  .submit-row .sr-info i { color: var(--red); }

  /* Sidebar */
  .notice-panel {
    background: linear-gradient(135deg, var(--red-dark) 0%, var(--red) 100%);
    color: #fff;
    border-radius: 14px;
    padding: 22px 18px;
    margin-bottom: 20px;
  }
  .notice-panel h6 { font-weight: 800; font-size: 14px; margin-bottom: 12px; }
  .notice-panel ul { padding-left: 16px; margin: 0; }
  .notice-panel ul li { font-size: 12.5px; margin-bottom: 6px; opacity: 0.9; }

  .form-floating-sat { position: relative; margin-bottom: 18px; }
  .help-block { font-size: 11.5px; color: #999; margin-top: 4px; }
</style>
{% endblock %}

{% block content %}

<!-- BANNER -->
<div class="page-banner">
  <div class="container">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('index') }}">Home</a></li>
        <li class="breadcrumb-item active">Student Registration</li>
      </ol>
    </nav>
    <h2><i class="fas fa-user-plus me-2"></i>Student Registration</h2>
    <p>CSC Scholarship Aptitude Test 2026 — Fill in your details to register</p>
  </div>
</div>

<div class="container pb-5">
  <div class="row g-4">
    <!-- FORM -->
    <div class="col-lg-8">
      <div class="reg-form-card">
        <div class="reg-form-header">
          <div class="fh-icon"><i class="fas fa-clipboard-list"></i></div>
          <div>
            <h3>SAT 2026 Registration Form</h3>
            <p>All fields marked with * are required</p>
          </div>
        </div>

        <form method="POST" action="{{ url_for('register') }}" id="regForm">
          <div class="reg-form-body">

            <!-- PERSONAL INFO -->
            <div class="section-divider">
              <span class="sd-label"><i class="fas fa-user me-1"></i>Personal Information</span>
              <hr>
            </div>

            <div class="row g-3">
              <div class="col-12">
                <label class="form-label-sat">Full Name <span class="required-star">*</span></label>
                <input type="text" class="form-control form-control-sat"
                  name="name" placeholder="Enter your full name"
                  value="{{ form.get('name', '') if form else '' }}" required>
                <div class="help-block">Enter name as it should appear on the admit card</div>
              </div>
              <div class="col-md-6">
                <label class="form-label-sat">Mobile Number <span class="required-star">*</span></label>
                <div class="input-group">
                  <span class="input-group-text" style="background:#f0f0f0;border-color:#ddd;font-size:13px;">+91</span>
                  <input type="tel" class="form-control form-control-sat" style="border-left:none;"
                    name="mobile" placeholder="10-digit mobile number"
                    maxlength="10" pattern="[0-9]{10}"
                    value="{{ form.get('mobile', '') if form else '' }}" required>
                </div>
                <div class="help-block">Used for admit card retrieval — must be valid</div>
              </div>
              <div class="col-md-6">
                <label class="form-label-sat">Gender <span class="required-star">*</span></label>
                <div class="gender-group">
                  <label class="gender-option">
                    <input type="radio" name="gender" value="Male" {% if form and form.get('gender') == 'Male' %}checked{% endif %} required>
                    <i class="fas fa-mars" style="color:var(--navy)"></i>
                    <span>Male</span>
                  </label>
                  <label class="gender-option">
                    <input type="radio" name="gender" value="Female" {% if form and form.get('gender') == 'Female' %}checked{% endif %}>
                    <i class="fas fa-venus" style="color:#c2185b"></i>
                    <span>Female</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- EXAM DETAILS -->
            <div class="section-divider">
              <span class="sd-label"><i class="fas fa-calendar-alt me-1"></i>Exam Details</span>
              <hr>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label-sat">Exam Centre <span class="required-star">*</span></label>
                <select class="form-select form-control-sat form-select-sat" name="exam_centre" required>
                  <option value="">-- Select Centre --</option>
                  {% for centre in centres %}
                  <option value="{{ centre }}" {% if form and form.get('exam_centre') == centre %}selected{% endif %}>{{ centre }}</option>
                  {% endfor %}
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label-sat">Exam Date <span class="required-star">*</span></label>
                <select class="form-select form-control-sat form-select-sat" name="exam_date" required>
                  <option value="">-- Select Date --</option>
                  {% for date in exam_dates %}
                  <option value="{{ date }}" {% if form and form.get('exam_date') == date %}selected{% endif %}>{{ date }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>

            <div class="mt-3">
              <label class="form-label-sat">Preferred Time Slot <span class="required-star">*</span></label>
              <div class="time-grid">
                {% for t in timings %}
                <label class="time-option">
                  <input type="radio" name="exam_time" value="{{ t }}" {% if form and form.get('exam_time') == t %}checked{% endif %} required>
                  {{ t }}
                </label>
                {% endfor %}
              </div>
            </div>

          </div><!-- /reg-form-body -->

          <div class="submit-row">
            <div class="sr-info">
              <i class="fas fa-shield-alt me-1"></i>
              Your information is secure and will only be used for SAT 2026 purposes.
            </div>
            <button type="submit" class="btn btn-sat-primary">
              <i class="fas fa-paper-plane me-2"></i>Submit Registration
            </button>
          </div>
        </form>
      </div><!-- /card -->
    </div>

    <!-- SIDEBAR -->
    <div class="col-lg-4">
      <div class="notice-panel">
        <h6><i class="fas fa-exclamation-circle me-2"></i>Important Instructions</h6>
        <ul>
          <li>Registration is FREE — no fees required</li>
          <li>Use a valid 10-digit mobile number</li>
          <li>Mobile number is used to retrieve admit card</li>
          <li>Report 30 min before exam time</li>
          <li>Carry printed admit card to exam</li>
        </ul>
      </div>

      <div class="sat-75-badge mb-3">
        <div class="win-text">WIN UP TO</div>
        <div class="pct">75%</div>
        <div class="scholarship">Scholarship</div>
        <div class="subtext">Free Admission Benefits</div>
      </div>

      <div style="background:#fff;border-radius:14px;padding:18px;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
        <div style="font-weight:700;color:var(--navy);margin-bottom:10px;font-size:13px;"><i class="fas fa-calendar-check me-1" style="color:var(--red)"></i>Available Dates</div>
        {% for date in exam_dates %}
        <div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:13px;color:#444;">
          <i class="fas fa-circle" style="font-size:6px;color:var(--red)"></i>{{ date }}
        </div>
        {% endfor %}
        <div style="font-weight:700;color:var(--navy);margin:14px 0 10px;font-size:13px;"><i class="fas fa-map-marker-alt me-1" style="color:var(--red)"></i>Exam Centres</div>
        {% for centre in centres %}
        <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:13px;color:#444;">
          <i class="fas fa-school" style="color:var(--red);font-size:12px;"></i>{{ centre }}
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>

{% endblock %}

{% block extra_js %}
<script>
// Time option click
document.querySelectorAll('.time-option').forEach(el => {
  el.addEventListener('click', function() {
    document.querySelectorAll('.time-option').forEach(x => x.classList.remove('selected'));
  });
});
// Mobile: digits only
document.querySelector('input[name=mobile]').addEventListener('input', function() {
  this.value = this.value.replace(/\D/g, '').slice(0, 10);
});
</script>
{% endblock %}
