(function () {
  'use strict';
  var api = window.ETL_API;
  if (!api) return;

  var loginBox = document.getElementById('admin-login');
  var passwordInput = document.getElementById('admin-password');
  var loginBtn = document.getElementById('admin-login-btn');
  var loginError = document.getElementById('admin-login-error');
  var loginErrorText = document.getElementById('admin-login-error-text');
  var panel = document.getElementById('admin-panel');
  var logoutBtn = document.getElementById('admin-logout-btn');
  var sittersList = document.getElementById('sitters-list');
  var bookingsList = document.getElementById('bookings-list');
  var tabs = document.querySelectorAll('.dash-tab');
  var tabpanels = document.querySelectorAll('.dash-tabpanel');

  var adminPassword = null;
  var cachedSitters = [];
  var cachedBookings = [];
  var clashNotices = {}; // bookingId -> [booking_ref, ...]

  var GENDER_LABELS = { female: 'Female', male: 'Male', prefer_not_to_say: 'Prefer not to say' };
  var RACE_LABELS = { black_african: 'Black African', coloured: 'Coloured', indian_asian: 'Indian / Asian', white: 'White', other: 'Other', prefer_not_to_say: 'Prefer not to say' };

  function headers() {
    return { 'X-Admin-Password': adminPassword };
  }

  function escapeHtml(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function fmtDate(iso) {
    if (!iso) return '\u2013';
    try {
      var d = new Date(iso);
      return d.toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) { return iso; }
  }

  // --- Login ---
  async function tryLogin() {
    var pwd = passwordInput.value;
    if (!pwd) return;
    loginBtn.disabled = true;
    loginBtn.textContent = 'Signing in\u2026';
    try {
      await api.postAuth('/api/admin/login', { password: pwd }, {});
      adminPassword = pwd;
      loginError.hidden = true;
      loginBox.hidden = true;
      panel.hidden = false;
      loadSitters();
      loadBookings();
    } catch (err) {
      loginErrorText.textContent = err.message || 'Incorrect password.';
      loginError.hidden = false;
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Sign in';
    }
  }
  loginBtn.addEventListener('click', tryLogin);
  passwordInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') tryLogin();
  });

  logoutBtn.addEventListener('click', function () {
    adminPassword = null;
    panel.hidden = true;
    loginBox.hidden = false;
    passwordInput.value = '';
  });

  // --- Tabs ---
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('is-active'); });
      tab.classList.add('is-active');
      var name = tab.getAttribute('data-tab');
      tabpanels.forEach(function (panelEl) {
        panelEl.hidden = panelEl.getAttribute('data-tabpanel') !== name;
      });
      if (name === 'calendar' && typeof renderAdminCalendar === 'function') renderAdminCalendar();
    });
  });

  function docLink(docType, recordId, hasDoc, kind, label) {
    if (hasDoc) {
      return '<button type="button" class="btn btn--ghost btn--sm" data-view-doc="' + docType + '" data-kind="' + kind + '" data-record="' + recordId + '">View ' + escapeHtml(label) + '</button>';
    }
    return '<span class="dash-docs__missing">' + escapeHtml(label) + ': not uploaded yet</span>';
  }

  async function openDocument(kind, recordId, docType) {
    var path = '/api/admin/' + kind + '/' + recordId + '/document/' + docType;
    var blob = await api.getBlobAuth(path, headers());
    var url = URL.createObjectURL(blob);
    window.open(url, '_blank');
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
  }

  function wireDocumentViewer(container) {
    container.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-view-doc]');
      if (!btn) return;
      var docType = btn.getAttribute('data-view-doc');
      var kind = btn.getAttribute('data-kind');
      var recordId = btn.getAttribute('data-record');
      var original = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Opening\u2026';
      openDocument(kind, recordId, docType).catch(function (err) {
        alert('Could not open document: ' + err.message);
      }).finally(function () {
        btn.disabled = false;
        btn.textContent = original;
      });
    });
  }
  wireDocumentViewer(sittersList);
  wireDocumentViewer(bookingsList);

  // --- Sitters ---
  var DOC_FIELDS = [
    ['id_doc_verified', 'ID / passport document checked'],
    ['proof_of_address_verified', 'Proof of address checked'],
    ['reference_verified', 'Reference contacted &amp; confirmed'],
    ['smile_id_verified', 'Smile ID verification complete'],
    ['registration_fee_paid', 'R99 registration fee received (Paystack)'],
  ];

  var SMILE_STATUS_LABELS = {
    not_configured: 'Not sent yet (Smile ID key not added)',
    submitted: 'Sent to Smile ID, awaiting result',
    received: 'Result received from Smile ID',
    error: 'Submission failed',
  };

  function smileIdSummary(r) {
    var status = r.smile_id_api_status || 'not_configured';
    var label = SMILE_STATUS_LABELS[status] || status;
    var parts = ['<strong>Smile ID status:</strong> ' + escapeHtml(label)];
    if (r.smile_id_job_id) parts.push('Job ID: ' + escapeHtml(r.smile_id_job_id));
    if (r.smile_id_result_summary) parts.push(escapeHtml(r.smile_id_result_summary));
    if (typeof r.liveness_frame_count === 'number') parts.push(r.liveness_frame_count + ' liveness frames captured');
    return '<div class="dash-smile-status">' + parts.join(' &middot; ') + '</div>';
  }

  async function loadSitters() {
    sittersList.innerHTML = '<div class="dash-empty">Loading babysitters\u2026</div>';
    try {
      var data = await api.getAuth('/api/admin/sitters', headers());
      cachedSitters = data.sitters || [];
      renderSitters(cachedSitters);
    } catch (err) {
      sittersList.innerHTML = '<div class="dash-empty">Could not load babysitters: ' + escapeHtml(err.message) + '</div>';
    }
  }

  function renderSitters(sitters) {
    if (!sitters.length) {
      sittersList.innerHTML = '<div class="dash-empty">No babysitter applications yet.</div>';
      return;
    }
    sittersList.innerHTML = sitters.map(function (s) {
      var verifiedBadge = s.verified
        ? '<span class="badge-verified"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg>Verified</span>'
        : '<span class="badge-verified badge-verified--pending"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>Pending</span>';
      var checklist = DOC_FIELDS.map(function (f) {
        var checked = s[f[0]] ? ' checked' : '';
        return '<label><input type="checkbox" data-doc="' + f[0] + '" data-sitter="' + s.id + '"' + checked + ' />' + f[1] + '</label>';
      }).join('');
      var photoHtml = s.has_selfie
        ? '<img class="dash-card__photo" data-sitter-photo="' + s.id + '" alt="' + escapeHtml(s.full_name) + ' profile photo" />'
        : '<div class="dash-card__photo dash-card__photo--placeholder">No photo</div>';
      var profileBits = [];
      if (s.profile_gender) profileBits.push(GENDER_LABELS[s.profile_gender] || s.profile_gender);
      if (s.profile_race) profileBits.push(RACE_LABELS[s.profile_race] || s.profile_race);
      if (s.profile_age) profileBits.push(s.profile_age + ' yrs');
      if (s.nationality) profileBits.push(escapeHtml(s.nationality));
      var profileLine = profileBits.length ? profileBits.join(' &middot; ') : 'Public profile not completed';
      return (
        '<div class="dash-card" data-sitter-card="' + s.id + '">' +
        '<div class="dash-card__head">' + photoHtml + '<div><div class="dash-card__title">' + escapeHtml(s.full_name) + '</div>' +
        '<div class="dash-card__meta">Applied ' + fmtDate(s.created_at) + ' &middot; ' + profileLine + '</div></div>' + verifiedBadge + '</div>' +
        '<dl class="dash-kv">' +
        '<div><dt>Email</dt><dd>' + escapeHtml(s.email) + '</dd></div>' +
        '<div><dt>Phone</dt><dd>' + escapeHtml(s.phone) + '</dd></div>' +
        '<div><dt>Experience level</dt><dd>Level ' + escapeHtml(s.experience_level) + ' &middot; ' + escapeHtml(s.years_experience) + '</dd></div>' +
        '<div><dt>Access code</dt><dd>' + escapeHtml(s.access_code || '\u2013') + '</dd></div>' +
        '<div><dt>ID type</dt><dd>' + escapeHtml(s.id_type === 'passport' ? ('Passport ' + (s.passport_number || '')) : ('SA ID ' + (s.id_number || ''))) + '</dd></div>' +
        '<div><dt>Reference</dt><dd>' + escapeHtml(s.reference_name || '\u2013') + '</dd></div>' +
        '</dl>' +
        '<div class="dash-checklist">' + checklist + '</div>' +
        smileIdSummary(s) +
        '<div class="dash-docs">' + docLink('id_document', s.id, s.has_id_document, 'sitters', 'ID / passport document') + docLink('proof_of_address', s.id, s.has_proof_of_address, 'sitters', 'Proof of address') + docLink('selfie', s.id, s.has_selfie, 'sitters', 'Selfie photo') + docLink('police_clearance', s.id, s.has_police_clearance, 'sitters', 'Police clearance certificate') + '</div>' +
        '<div class="field-grid field-grid--sitter-profile">' +
        '<div class="field"><label for="rating-' + s.id + '">Star rating (0&ndash;5)</label><input type="number" id="rating-' + s.id + '" data-rating="' + s.id + '" min="0" max="5" step="0.1" value="' + (s.rating || 0) + '" /></div>' +
        '<div class="field"><label for="gender-' + s.id + '">Gender</label><select id="gender-' + s.id + '" data-profile-gender="' + s.id + '">' +
          '<option value="">Not set</option>' +
          Object.keys(GENDER_LABELS).map(function (k) { return '<option value="' + k + '"' + (s.profile_gender === k ? ' selected' : '') + '>' + GENDER_LABELS[k] + '</option>'; }).join('') +
          '</select></div>' +
        '<div class="field"><label for="race-' + s.id + '">Race</label><select id="race-' + s.id + '" data-profile-race="' + s.id + '">' +
          '<option value="">Not set</option>' +
          Object.keys(RACE_LABELS).map(function (k) { return '<option value="' + k + '"' + (s.profile_race === k ? ' selected' : '') + '>' + RACE_LABELS[k] + '</option>'; }).join('') +
          '</select></div>' +
        '<div class="field"><label for="age-' + s.id + '">Age</label><input type="number" id="age-' + s.id + '" data-profile-age="' + s.id + '" min="18" max="80" value="' + (s.profile_age || '') + '" /></div>' +
        '</div>' +
        '<div class="dash-notes"><textarea data-notes="' + s.id + '" placeholder="Admin notes (e.g. how documents were checked)">' + escapeHtml(s.admin_notes || '') + '</textarea></div>' +
        '<div class="dash-card__actions">' +
        '<button type="button" class="btn btn--primary btn--sm" data-save-sitter="' + s.id + '">Save verification</button>' +
        '</div>' +
        '</div>'
      );
    }).join('');
    loadSitterPhotos(sitters);
  }

  function loadSitterPhotos(sitters) {
    sitters.forEach(function (s) {
      if (!s.has_selfie) return;
      var img = sittersList.querySelector('[data-sitter-photo="' + s.id + '"]');
      if (!img) return;
      api.getBlobAuth('/api/admin/sitters/' + s.id + '/document/selfie', headers()).then(function (blob) {
        img.src = URL.createObjectURL(blob);
      }).catch(function () {
        img.replaceWith(Object.assign(document.createElement('div'), { className: 'dash-card__photo dash-card__photo--placeholder', textContent: 'No photo' }));
      });
    });
  }

  sittersList.addEventListener('click', async function (e) {
    var btn = e.target.closest('[data-save-sitter]');
    if (!btn) return;
    var id = btn.getAttribute('data-save-sitter');
    var card = sittersList.querySelector('[data-sitter-card="' + id + '"]');
    var payload = {};
    DOC_FIELDS.forEach(function (f) {
      var box = card.querySelector('[data-doc="' + f[0] + '"]');
      payload[f[0]] = !!(box && box.checked);
    });
    var notesEl = card.querySelector('[data-notes="' + id + '"]');
    payload.admin_notes = notesEl ? notesEl.value : '';
    var ratingEl = card.querySelector('[data-rating="' + id + '"]');
    if (ratingEl && ratingEl.value !== '') payload.rating = parseFloat(ratingEl.value);
    var genderEl = card.querySelector('[data-profile-gender="' + id + '"]');
    if (genderEl && genderEl.value !== '') payload.profile_gender = genderEl.value;
    var raceEl = card.querySelector('[data-profile-race="' + id + '"]');
    if (raceEl && raceEl.value !== '') payload.profile_race = raceEl.value;
    var ageEl = card.querySelector('[data-profile-age="' + id + '"]');
    if (ageEl && ageEl.value !== '') payload.profile_age = parseInt(ageEl.value, 10);
    btn.disabled = true;
    btn.textContent = 'Saving\u2026';
    try {
      await api.postAuth('/api/admin/sitters/' + id + '/verify', payload, headers());
      await loadSitters();
      await loadBookings(); // sitter dropdowns may need refreshed verified state
    } catch (err) {
      alert('Could not save: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Save verification';
    }
  });

  // --- Bookings ---
  var FAMILY_FIELDS = [
    ['family_id_verified', 'Family ID document checked'],
    ['family_proof_of_address_verified', 'Family proof of address checked'],
    ['registration_fee_paid', 'R99 registration fee received (Paystack)'],
  ];

  async function loadBookings() {
    bookingsList.innerHTML = '<div class="dash-empty">Loading bookings\u2026</div>';
    try {
      var data = await api.getAuth('/api/admin/bookings', headers());
      cachedBookings = data.bookings || [];
      renderBookings(cachedBookings);
      if (typeof renderAdminCalendar === 'function') renderAdminCalendar();
    } catch (err) {
      bookingsList.innerHTML = '<div class="dash-empty">Could not load bookings: ' + escapeHtml(err.message) + '</div>';
    }
  }

  function sitterOptions(selectedId) {
    var opts = '<option value="">\u2014 Not assigned \u2014</option>';
    cachedSitters.forEach(function (s) {
      var sel = String(s.id) === String(selectedId) ? ' selected' : '';
      var label = s.full_name + (s.verified ? ' \u2713 verified' : ' (unverified)');
      opts += '<option value="' + s.id + '"' + sel + '>' + escapeHtml(label) + '</option>';
    });
    return opts;
  }

  function renderBookings(bookings) {
    if (!bookings.length) {
      bookingsList.innerHTML = '<div class="dash-empty">No bookings yet.</div>';
      return;
    }
    bookingsList.innerHTML = bookings.map(function (b) {
      var checklist = FAMILY_FIELDS.map(function (f) {
        var checked = b[f[0]] ? ' checked' : '';
        return '<label><input type="checkbox" data-fdoc="' + f[0] + '" data-booking="' + b.id + '"' + checked + ' />' + f[1] + '</label>';
      }).join('');
      var respBadge = '';
      if (b.assigned_sitter_id) {
        if (b.sitter_response === 'accepted') respBadge = '<span class="status-pill status-pill--done">Accepted by sitter</span>';
        else if (b.sitter_response === 'declined') respBadge = '<span class="status-pill">Declined by sitter</span>';
        else respBadge = '<span class="status-pill status-pill--pending">Awaiting sitter response</span>';
      }
      var petLine = b.has_pets
        ? '<div><dt>Pets</dt><dd>Yes &mdash; ' + escapeHtml(b.pet_type || 'type not specified') + '</dd></div>'
        : '<div><dt>Pets</dt><dd>No pets at home</dd></div>';
      var specialBits = [];
      if (b.special_bath_baby) specialBits.push('Bath the baby/child');
      if (b.special_feed_baby) specialBits.push('Feed the baby/child');
      var specialLine = specialBits.length
        ? '<div><dt>Requested duties</dt><dd>' + specialBits.map(escapeHtml).join(', ') + '</dd></div>'
        : '';
      var instructionsLine = b.special_instructions
        ? '<p class="dash-card__meta" style="margin-bottom: var(--space-2);"><strong>Care instructions:</strong> ' + escapeHtml(b.special_instructions) + '</p>'
        : '';
      var precautionsLine = b.special_precautions
        ? '<p class="dash-card__meta" style="margin-bottom: var(--space-4);"><strong>Precautions:</strong> ' + escapeHtml(b.special_precautions) + '</p>'
        : '';
      var preferredLine = b.preferred_sitter
        ? '<div><dt>Family\u2019s preferred sitter</dt><dd>' + escapeHtml(b.preferred_sitter.full_name) + (b.preferred_sitter.verified ? ' \u2713 verified' : ' (unverified)') + '</dd></div>'
        : '';
      return (
        '<div class="dash-card" data-booking-card="' + b.id + '">' +
        '<div class="dash-card__head"><div><div class="dash-card__title">' + escapeHtml(b.parent_name) + ' &middot; ' + escapeHtml(b.booking_ref) + '</div>' +
        '<div class="dash-card__meta">' + fmtDate(b.booking_date) + ' at ' + escapeHtml(b.start_time) + ' &middot; ' + escapeHtml(b.duration_hours) + 'h &middot; Level ' + escapeHtml(b.level) + '</div></div>' + respBadge + '</div>' +
        '<dl class="dash-kv">' +
        '<div><dt>Phone</dt><dd>' + escapeHtml(b.phone) + '</dd></div>' +
        '<div><dt>Address</dt><dd>' + escapeHtml(b.address) + '</dd></div>' +
        '<div><dt>Children</dt><dd>' + escapeHtml(b.children_count) + '</dd></div>' +
        petLine + specialLine + preferredLine +
        '</dl>' +
        instructionsLine +
        precautionsLine +
        '<div class="dash-checklist">' + checklist + '</div>' +
        smileIdSummary(b) +
        '<div class="dash-docs">' + docLink('id_document', b.id, b.has_id_document, 'bookings', 'ID / passport document') + docLink('proof_of_address', b.id, b.has_proof_of_address, 'bookings', 'Proof of address') + docLink('selfie', b.id, b.has_selfie, 'bookings', 'Selfie photo') + '</div>' +
        '<div class="dash-card__actions">' +
        '<select data-sitter-select="' + b.id + '">' + sitterOptions(b.assigned_sitter_id) + '</select>' +
        '<button type="button" class="btn btn--secondary btn--sm" data-assign="' + b.id + '">Assign</button>' +
        '<button type="button" class="btn btn--ghost btn--sm" data-save-family="' + b.id + '">Save family checks</button>' +
        '</div>' +
        '<div id="clash-' + b.id + '">' + (clashNotices[b.id] && clashNotices[b.id].length
          ? '<div class="clash-warning">Schedule clash: this sitter is already booked for ' + clashNotices[b.id].map(escapeHtml).join(', ') + ' around this time. Double-check before confirming.</div>'
          : '') + '</div>' +
        '</div>'
      );
    }).join('');
  }

  bookingsList.addEventListener('click', async function (e) {
    var assignBtn = e.target.closest('[data-assign]');
    var saveBtn = e.target.closest('[data-save-family]');
    if (assignBtn) {
      var bId = assignBtn.getAttribute('data-assign');
      var select = bookingsList.querySelector('[data-sitter-select="' + bId + '"]');
      var sitterId = select.value;
      assignBtn.disabled = true;
      assignBtn.textContent = 'Assigning\u2026';
      try {
        var res;
        if (!sitterId) {
          res = await api.postAuth('/api/admin/bookings/' + bId + '/unassign', {}, headers());
        } else {
          res = await api.postAuth('/api/admin/bookings/' + bId + '/assign', { sitter_id: parseInt(sitterId, 10) }, headers());
        }
        clashNotices[bId] = (res && res.clashes) || [];
        await loadBookings();
      } catch (err) {
        alert('Could not assign: ' + err.message);
      } finally {
        assignBtn.disabled = false;
        assignBtn.textContent = 'Assign';
      }
    } else if (saveBtn) {
      var fId = saveBtn.getAttribute('data-save-family');
      var card = bookingsList.querySelector('[data-booking-card="' + fId + '"]');
      var payload = {};
      FAMILY_FIELDS.forEach(function (f) {
        var box = card.querySelector('[data-fdoc="' + f[0] + '"]');
        payload[f[0]] = !!(box && box.checked);
      });
      saveBtn.disabled = true;
      saveBtn.textContent = 'Saving\u2026';
      try {
        await api.postAuth('/api/admin/bookings/' + fId + '/verify', payload, headers());
        await loadBookings();
      } catch (err) {
        alert('Could not save: ' + err.message);
      } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save family checks';
      }
    }
  });

  // --- Calendar tab (all months, built from cached bookings) ---
  var adminCalGrid = document.getElementById('admin-cal-grid');
  var adminCalTitle = document.getElementById('admin-cal-title');
  var adminCalPrevBtn = document.getElementById('admin-cal-prev');
  var adminCalNextBtn = document.getElementById('admin-cal-next');
  var adminCalDayDetail = document.getElementById('admin-cal-day-detail');
  var adminCalToday = new Date();
  var adminCalYear = adminCalToday.getFullYear();
  var adminCalMonth = adminCalToday.getMonth();
  var adminCalSelectedDate = null;

  function renderAdminCalendar() {
    if (!adminCalGrid) return;
    var year = adminCalYear;
    var month = adminCalMonth;
    adminCalTitle.textContent = new Date(year, month, 1).toLocaleDateString('en-ZA', { month: 'long', year: 'numeric' });

    var byDate = {};
    cachedBookings.forEach(function (b) {
      var d = b.booking_date;
      if (!d) return;
      if (!byDate[d]) byDate[d] = [];
      byDate[d].push(b);
    });

    var firstDay = new Date(year, month, 1);
    var startWeekday = firstDay.getDay();
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var todayStr = adminCalToday.toISOString().slice(0, 10);

    var html = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(function (d) {
      return '<div class="mini-cal__dow">' + d + '</div>';
    }).join('');

    for (var i = 0; i < startWeekday; i++) {
      html += '<div class="mini-cal__day mini-cal__day--empty"></div>';
    }
    for (var day = 1; day <= daysInMonth; day++) {
      var dateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');
      var dayBookings = byDate[dateStr] || [];
      var cls = 'mini-cal__day';
      if (dateStr === todayStr) cls += ' mini-cal__day--today';
      if (dayBookings.length) {
        var hasPending = dayBookings.some(function (b) { return !b.assigned_sitter_id; });
        cls += hasPending ? ' mini-cal__day--unavailable' : ' mini-cal__day--booked';
      }
      if (dateStr === adminCalSelectedDate) cls += ' mini-cal__day--selected';
      html += '<div class="' + cls + '" data-admin-cal-date="' + dateStr + '">' + day +
        (dayBookings.length ? '<span class="mini-cal__day-count">' + dayBookings.length + '</span>' : '') +
        '</div>';
    }
    adminCalGrid.innerHTML = html;

    if (adminCalSelectedDate) {
      renderAdminCalDayDetail(adminCalSelectedDate, byDate[adminCalSelectedDate] || []);
    }
  }

  function renderAdminCalDayDetail(dateStr, bookings) {
    if (!adminCalDayDetail) return;
    if (!bookings.length) {
      adminCalDayDetail.hidden = false;
      adminCalDayDetail.innerHTML = '<div class="dash-empty">No bookings on ' + escapeHtml(dateStr) + '.</div>';
      return;
    }
    adminCalDayDetail.hidden = false;
    adminCalDayDetail.innerHTML = '<h4>Bookings on ' + escapeHtml(dateStr) + '</h4>' + bookings.map(function (b) {
      var sitterName = b.assigned_sitter ? escapeHtml(b.assigned_sitter.full_name) : 'Not yet assigned';
      return (
        '<div class="dash-card dash-card--compact">' +
        '<div class="dash-card__title">' + escapeHtml(b.parent_name) + ' &middot; ' + escapeHtml(b.booking_ref) + '</div>' +
        '<div class="dash-card__meta">' + escapeHtml(b.start_time) + ' &middot; ' + escapeHtml(b.duration_hours) + 'h &middot; Level ' + escapeHtml(b.level) + ' &middot; Sitter: ' + sitterName + '</div>' +
        '</div>'
      );
    }).join('');
  }

  if (adminCalGrid) {
    adminCalGrid.addEventListener('click', function (e) {
      var cell = e.target.closest('[data-admin-cal-date]');
      if (!cell) return;
      adminCalSelectedDate = cell.getAttribute('data-admin-cal-date');
      renderAdminCalendar();
    });
  }
  if (adminCalPrevBtn) {
    adminCalPrevBtn.addEventListener('click', function () {
      adminCalMonth -= 1;
      if (adminCalMonth < 0) { adminCalMonth = 11; adminCalYear -= 1; }
      renderAdminCalendar();
    });
  }
  if (adminCalNextBtn) {
    adminCalNextBtn.addEventListener('click', function () {
      adminCalMonth += 1;
      if (adminCalMonth > 11) { adminCalMonth = 0; adminCalYear += 1; }
      renderAdminCalendar();
    });
  }

  // --- Manual booking modal ---
  var manualModal = document.getElementById('manual-booking-modal');
  var openManualBtn = document.getElementById('open-manual-booking-btn');
  var closeManualBtn = document.getElementById('close-manual-booking-btn');
  var manualForm = document.getElementById('manual-booking-form');
  var manualError = document.getElementById('manual-booking-error');
  var manualErrorText = document.getElementById('manual-booking-error-text');
  var manualSubmitBtn = document.getElementById('manual-booking-submit');
  var manualSitterSelect = document.getElementById('mb_assign_sitter_id');

  function openManualModal() {
    if (!manualModal) return;
    var opts = '<option value="">\u2014 Don\u2019t assign yet \u2014</option>';
    cachedSitters.forEach(function (s) {
      var label = s.full_name + (s.verified ? ' \u2713 verified' : ' (unverified)');
      opts += '<option value="' + s.id + '">' + escapeHtml(label) + '</option>';
    });
    if (manualSitterSelect) manualSitterSelect.innerHTML = opts;
    manualError.hidden = true;
    manualForm.reset();
    manualModal.hidden = false;
  }
  function closeManualModal() {
    if (manualModal) manualModal.hidden = true;
  }
  if (openManualBtn) openManualBtn.addEventListener('click', openManualModal);
  if (closeManualBtn) closeManualBtn.addEventListener('click', closeManualModal);
  if (manualModal) {
    manualModal.addEventListener('click', function (e) {
      if (e.target === manualModal) closeManualModal();
    });
  }

  if (manualForm) {
    manualForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      var fd = new FormData(manualForm);
      var payload = {
        parent_name: fd.get('parent_name') || '',
        phone: fd.get('phone') || '',
        email: fd.get('email') || '',
        address: fd.get('address') || '',
        children_count: fd.get('children_count') || '',
        rate_type: fd.get('rate_type') || 'day',
        level: String(fd.get('level') || '1'),
        hourly_rate: parseFloat(fd.get('hourly_rate')),
        duration_hours: parseFloat(fd.get('duration_hours')),
        booking_date: fd.get('booking_date') || '',
        start_time: fd.get('start_time') || '',
        has_pets: !!fd.get('has_pets'),
        pet_type: fd.get('pet_type') || '',
        special_bath_baby: !!fd.get('special_bath_baby'),
        special_feed_baby: !!fd.get('special_feed_baby'),
        special_instructions: fd.get('special_instructions') || '',
        admin_notes: fd.get('admin_notes') || '',
      };
      var assignId = fd.get('assign_sitter_id');
      if (assignId) payload.assign_sitter_id = parseInt(assignId, 10);
      manualSubmitBtn.disabled = true;
      manualSubmitBtn.textContent = 'Creating\u2026';
      manualError.hidden = true;
      try {
        await api.postAuth('/api/admin/bookings/manual', payload, headers());
        closeManualModal();
        await loadBookings();
      } catch (err) {
        manualErrorText.textContent = err.message || 'Could not create the booking.';
        manualError.hidden = false;
      } finally {
        manualSubmitBtn.disabled = false;
        manualSubmitBtn.textContent = 'Create booking';
      }
    });
  }
})();
