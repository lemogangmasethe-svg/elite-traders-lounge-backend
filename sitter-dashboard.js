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
    } catch (err) {
      bookingsList.innerHTML = '<div class="dash-empty">Could not load bookings: ' + escapeHtml(err.message) + '</div>';
    }
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
