(function () {
  'use strict';
  var api = window.ETL_API;
  if (!api) return;

  var loginBox = document.getElementById('sitter-login');
  var emailInput = document.getElementById('sitter-login-email');
  var codeInput = document.getElementById('sitter-login-code');
  var loginBtn = document.getElementById('sitter-login-btn');
  var loginError = document.getElementById('sitter-login-error');
  var loginErrorText = document.getElementById('sitter-login-error-text');
  var panel = document.getElementById('sitter-panel');
  var whoEl = document.getElementById('sitter-who');
  var logoutBtn = document.getElementById('sitter-logout-btn');
  var bookingsList = document.getElementById('sitter-bookings-list');
  var calGrid = document.getElementById('mini-cal-grid');
  var calTitle = document.getElementById('mini-cal-title');
  var calPrevBtn = document.getElementById('mini-cal-prev');
  var calNextBtn = document.getElementById('mini-cal-next');
  var verifStatusBox = document.getElementById('sitter-verification-status');
  var renewalBox = document.getElementById('sitter-renewal-box');
  var renewalToggle = document.getElementById('sitter-renewal-toggle');
  var renewalForm = document.getElementById('sitter-renewal-form');
  var renewalForeignField = document.getElementById('sitter-renewal-foreign-field');
  var renewalSubmitBtn = document.getElementById('sitter-renewal-submit');
  var renewalError = document.getElementById('sitter-renewal-error');
  var renewalErrorText = document.getElementById('sitter-renewal-error-text');
  var renewalSuccess = document.getElementById('sitter-renewal-success');
  var renewalPayLink = document.getElementById('sitter-renewal-pay-link');
  var MAX_DOCUMENT_BYTES = 6 * 1024 * 1024;
  var ALLOWED_DOCUMENT_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf'];

  var creds = null; // { email, access_code }
  var lastSitter = null;
  var lastBookings = [];
  var calToday = new Date();
  var calYear = calToday.getFullYear();
  var calMonth = calToday.getMonth();

  function escapeHtml(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function fmtDate(iso) {
    if (!iso) return '\u2013';
    try {
      var d = new Date(iso + 'T00:00:00');
      return d.toLocaleDateString('en-ZA', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) { return iso; }
  }

  async function tryLogin() {
    var email = emailInput.value.trim();
    var code = codeInput.value.trim().toUpperCase();
    if (!email || !code) return;
    loginBtn.disabled = true;
    loginBtn.textContent = 'Signing in\u2026';
    try {
      var sitter = await api.post('/api/sitter/login', { email: email, access_code: code });
      creds = { email: email, access_code: code };
      loginError.hidden = true;
      loginBox.hidden = true;
      panel.hidden = false;
      whoEl.textContent = 'Signed in as ' + sitter.full_name;
      loadBookings();
    } catch (err) {
      loginErrorText.textContent = err.message || "That email and access code don't match.";
      loginError.hidden = false;
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Sign in';
    }
  }
  loginBtn.addEventListener('click', tryLogin);
  [emailInput, codeInput].forEach(function (el) {
    el.addEventListener('keydown', function (e) { if (e.key === 'Enter') tryLogin(); });
  });

  logoutBtn.addEventListener('click', function () {
    creds = null;
    panel.hidden = true;
    loginBox.hidden = false;
    emailInput.value = '';
    codeInput.value = '';
  });

  async function loadBookings() {
    bookingsList.innerHTML = '<div class="dash-empty">Loading your bookings\u2026</div>';
    try {
      var data = await api.post('/api/sitter/bookings', creds);
      lastSitter = data.sitter;
      lastBookings = data.bookings || [];
      whoEl.textContent = 'Signed in as ' + lastSitter.full_name;
      renderBookings(lastBookings);
      renderCalendar();
      renderVerificationStatus(lastSitter);
    } catch (err) {
      bookingsList.innerHTML = '<div class="dash-empty">Could not load bookings: ' + escapeHtml(err.message) + '</div>';
    }
  }

  var VERIFICATION_STATUS_LABELS = {
    current: 'Your verification is current.',
    due_soon: 'Your annual renewal is coming up soon.',
    overdue: 'Your verification has lapsed \u2014 you will not appear to families until you renew.',
    unknown: 'We do not have a renewal date on file yet.',
  };

  function renderVerificationStatus(sitter) {
    if (!verifStatusBox || !sitter) return;
    var status = sitter.verification_status || 'unknown';
    var label = VERIFICATION_STATUS_LABELS[status] || status;
    var badgeClass = 'badge-renewal badge-renewal--' + status.replace(/_/g, '-');
    var badgeLabel = status === 'overdue' ? 'Renewal overdue' : (status === 'due_soon' ? 'Renewal due soon' : (status === 'current' ? 'Current' : 'Unknown'));
    var html = '<span class="' + badgeClass + '">' + escapeHtml(badgeLabel) + '</span>';
    html += '<p class="dash-card__meta" style="margin-top: var(--space-3);">' + escapeHtml(label);
    if (sitter.verification_due_date) {
      html += ' Documents are due by <strong>' + fmtDate(sitter.verification_due_date) + '</strong>';
      if (typeof sitter.verification_days_left === 'number' && status !== 'overdue') {
        html += ' (' + sitter.verification_days_left + ' day' + (sitter.verification_days_left === 1 ? '' : 's') + ' left)';
      }
      html += '.';
    }
    html += '</p>';
    html += '<p class="dash-card__meta">R99 annual fee: ' + (sitter.registration_fee_paid ? ('paid on ' + fmtDate(sitter.fee_paid_at)) : 'not yet confirmed as paid') + '.</p>';
    verifStatusBox.innerHTML = html;
    if (renewalBox) renewalBox.hidden = false;
    if (renewalForeignField) renewalForeignField.hidden = sitter.id_type !== 'passport';
    var renewForeignInput = document.getElementById('renew_foreign_police_clearance_document');
    if (renewForeignInput) renewForeignInput.required = sitter.id_type === 'passport';
  }

  if (renewalToggle && renewalForm) {
    renewalToggle.addEventListener('click', function () {
      renewalForm.hidden = !renewalForm.hidden;
      renewalToggle.textContent = renewalForm.hidden ? 'Submit renewal documents' : 'Hide renewal form';
    });
  }

  function readFileAsBase64(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        var result = reader.result || '';
        var commaIndex = result.indexOf(',');
        resolve(commaIndex >= 0 ? result.slice(commaIndex + 1) : result);
      };
      reader.onerror = function () { reject(new Error('Could not read the file. Please try again.')); };
      reader.readAsDataURL(file);
    });
  }

  var RENEWAL_DOCUMENT_LABELS = {
    police_clearance: 'AFIS check or police clearance certificate',
    child_protection_clearance: 'Child Protection Register (Part B) clearance letter',
    foreign_police_clearance: 'foreign police clearance certificate',
  };

  async function buildRenewalDocumentFields(prefix, input) {
    var label = RENEWAL_DOCUMENT_LABELS[prefix] || prefix;
    var file = input && input.files && input.files[0];
    if (!file) throw new Error('Please upload your ' + label + '.');
    if (ALLOWED_DOCUMENT_TYPES.indexOf(file.type) === -1) {
      throw new Error('Please upload your ' + label + ' as a JPG, PNG, or PDF file.');
    }
    if (file.size > MAX_DOCUMENT_BYTES) {
      throw new Error('Your ' + label + ' file is too large. Please keep it under 6MB.');
    }
    var data = await readFileAsBase64(file);
    var fields = {};
    fields[prefix + '_data'] = data;
    fields[prefix + '_filename'] = file.name;
    fields[prefix + '_mimetype'] = file.type;
    return fields;
  }

  if (renewalForm) {
    renewalForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (renewalError) renewalError.hidden = true;
      if (renewalSuccess) renewalSuccess.hidden = true;
      renewalSubmitBtn.disabled = true;
      renewalSubmitBtn.textContent = 'Submitting\u2026';
      try {
        var policeFields = await buildRenewalDocumentFields('police_clearance', document.getElementById('renew_police_clearance_document'));
        var cprFields = await buildRenewalDocumentFields('child_protection_clearance', document.getElementById('renew_child_protection_clearance_document'));
        var foreignFields = (lastSitter && lastSitter.id_type === 'passport')
          ? await buildRenewalDocumentFields('foreign_police_clearance', document.getElementById('renew_foreign_police_clearance_document'))
          : {};
        var payload = Object.assign({}, creds, policeFields, cprFields, foreignFields);
        var result = await api.post('/api/sitter/renew-verification', payload);
        lastSitter = result.sitter || lastSitter;
        renderVerificationStatus(lastSitter);
        if (renewalSuccess) renewalSuccess.hidden = false;
        if (renewalPayLink) renewalPayLink.hidden = false;
        renewalForm.reset();
      } catch (err) {
        if (renewalErrorText) renewalErrorText.textContent = err.message || 'Something went wrong. Please try again.';
        if (renewalError) renewalError.hidden = false;
      } finally {
        renewalSubmitBtn.disabled = false;
        renewalSubmitBtn.textContent = 'Submit renewal documents';
      }
    });
  }

  function renderBookings(bookings) {
    var relevant = bookings.filter(function (b) { return b.status === 'assigned' || b.status === 'confirmed'; });
    if (!relevant.length) {
      bookingsList.innerHTML = '<div class="dash-empty">No bookings assigned to you right now.</div>';
      return;
    }
    bookingsList.innerHTML = relevant.map(function (b) {
      var pill;
      if (b.sitter_response === 'accepted') pill = '<span class="status-pill status-pill--done">Accepted</span>';
      else if (b.sitter_response === 'declined') pill = '<span class="status-pill">Declined</span>';
      else pill = '<span class="status-pill status-pill--pending">Awaiting your response</span>';
      var actions = '';
      if (b.sitter_response === 'pending') {
        actions =
          '<button type="button" class="btn btn--primary btn--sm" data-respond="accepted" data-booking="' + b.id + '">Accept</button>' +
          '<button type="button" class="btn btn--ghost btn--sm" data-respond="declined" data-booking="' + b.id + '">Decline</button>';
      } else {
        actions = '<button type="button" class="btn btn--ghost btn--sm" data-respond="' + (b.sitter_response === 'accepted' ? 'declined' : 'accepted') + '" data-booking="' + b.id + '">' + (b.sitter_response === 'accepted' ? 'Change to decline' : 'Change to accept') + '</button>';
      }
      return (
        '<div class="dash-card">' +
        '<div class="dash-card__head"><div><div class="dash-card__title">' + fmtDate(b.booking_date) + ' at ' + escapeHtml(b.start_time) + '</div>' +
        '<div class="dash-card__meta">Booking ' + escapeHtml(b.booking_ref) + ' &middot; ' + escapeHtml(b.duration_hours) + 'h &middot; Level ' + escapeHtml(b.level) + ' ' + escapeHtml(b.rate_type) + '</div></div>' + pill + '</div>' +
        '<dl class="dash-kv">' +
        '<div><dt>Family</dt><dd>' + escapeHtml(b.parent_name) + '</dd></div>' +
        '<div><dt>Phone</dt><dd>' + escapeHtml(b.phone) + '</dd></div>' +
        '<div><dt>Address</dt><dd>' + escapeHtml(b.address) + '</dd></div>' +
        '<div><dt>Children</dt><dd>' + escapeHtml(b.children_count) + '</dd></div>' +
        '</dl>' +
        (b.special_instructions ? '<p class="dash-card__meta" style="margin-bottom: var(--space-4);">' + escapeHtml(b.special_instructions) + '</p>' : '') +
        '<div class="dash-card__actions">' + actions + '</div>' +
        '</div>'
      );
    }).join('');
  }

  bookingsList.addEventListener('click', async function (e) {
    var btn = e.target.closest('[data-respond]');
    if (!btn) return;
    var id = btn.getAttribute('data-booking');
    var response = btn.getAttribute('data-respond');
    btn.disabled = true;
    try {
      await api.post('/api/sitter/bookings/' + id + '/respond', Object.assign({}, creds, { response: response }));
      await loadBookings();
    } catch (err) {
      alert('Could not update: ' + err.message);
      btn.disabled = false;
    }
  });

  // --- Calendar ---
  function renderCalendar() {
    if (!lastSitter) return;
    var today = calToday;
    var year = calYear;
    var month = calMonth;
    calTitle.textContent = new Date(year, month, 1).toLocaleDateString('en-ZA', { month: 'long', year: 'numeric' });

    var bookedDates = {};
    lastBookings.forEach(function (b) {
      if ((b.status === 'assigned' || b.status === 'confirmed') && b.sitter_response === 'accepted') {
        bookedDates[b.booking_date] = true;
      }
    });
    var unavailable = {};
    (lastSitter.unavailable_dates || []).forEach(function (d) { unavailable[d] = true; });

    var firstDay = new Date(year, month, 1);
    var startWeekday = firstDay.getDay();
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var todayStr = today.toISOString().slice(0, 10);

    var html = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(function (d) {
      return '<div class="mini-cal__dow">' + d + '</div>';
    }).join('');

    for (var i = 0; i < startWeekday; i++) {
      html += '<div class="mini-cal__day mini-cal__day--empty"></div>';
    }
    for (var day = 1; day <= daysInMonth; day++) {
      var dateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');
      var cls = 'mini-cal__day';
      var isPast = dateStr < todayStr;
      if (bookedDates[dateStr]) {
        cls += ' mini-cal__day--booked';
      } else if (unavailable[dateStr]) {
        cls += ' mini-cal__day--unavailable';
      }
      if (isPast) cls += ' mini-cal__day--past';
      var clickable = !bookedDates[dateStr] && !isPast;
      html += '<div class="' + cls + '"' + (clickable ? ' data-cal-date="' + dateStr + '"' : '') + '>' + day + '</div>';
    }
    calGrid.innerHTML = html;
  }

  calGrid.addEventListener('click', async function (e) {
    var cell = e.target.closest('[data-cal-date]');
    if (!cell) return;
    var dateStr = cell.getAttribute('data-cal-date');
    var isUnavailable = cell.classList.contains('mini-cal__day--unavailable');
    var action = isUnavailable ? 'remove' : 'add';
    try {
      var res = await api.post('/api/sitter/unavailability', Object.assign({}, creds, { date: dateStr, action: action }));
      lastSitter.unavailable_dates = res.unavailable_dates || [];
      renderCalendar();
    } catch (err) {
      alert('Could not update availability: ' + err.message);
    }
  });

  if (calPrevBtn) {
    calPrevBtn.addEventListener('click', function () {
      calMonth -= 1;
      if (calMonth < 0) { calMonth = 11; calYear -= 1; }
      renderCalendar();
    });
  }
  if (calNextBtn) {
    calNextBtn.addEventListener('click', function () {
      calMonth += 1;
      if (calMonth > 11) { calMonth = 0; calYear += 1; }
      renderCalendar();
    });
  }
})();
