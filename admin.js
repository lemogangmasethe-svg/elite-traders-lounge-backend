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
  var clashNotices = {}; // bookingId -> [booking_ref, ...]

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
  ];

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
      return (
        '<div class="dash-card" data-sitter-card="' + s.id + '">' +
        '<div class="dash-card__head"><div><div class="dash-card__title">' + escapeHtml(s.full_name) + '</div>' +
        '<div class="dash-card__meta">Applied ' + fmtDate(s.created_at) + '</div></div>' + verifiedBadge + '</div>' +
        '<dl class="dash-kv">' +
        '<div><dt>Email</dt><dd>' + escapeHtml(s.email) + '</dd></div>' +
        '<div><dt>Phone</dt><dd>' + escapeHtml(s.phone) + '</dd></div>' +
        '<div><dt>Experience level</dt><dd>Level ' + escapeHtml(s.experience_level) + ' &middot; ' + escapeHtml(s.years_experience) + '</dd></div>' +
        '<div><dt>Access code</dt><dd>' + escapeHtml(s.access_code || '\u2013') + '</dd></div>' +
        '<div><dt>ID type</dt><dd>' + escapeHtml(s.id_type === 'passport' ? ('Passport ' + (s.passport_number || '')) : ('SA ID ' + (s.id_number || ''))) + '</dd></div>' +
        '<div><dt>Reference</dt><dd>' + escapeHtml(s.reference_name || '\u2013') + '</dd></div>' +
        '</dl>' +
        '<div class="dash-checklist">' + checklist + '</div>' +
        '<div class="dash-docs">' + docLink('id_document', s.id, s.has_id_document, 'sitters', 'ID / passport document') + docLink('proof_of_address', s.id, s.has_proof_of_address, 'sitters', 'Proof of address') + '</div>' +
        '<div class="dash-notes"><textarea data-notes="' + s.id + '" placeholder="Admin notes (e.g. how documents were checked)">' + escapeHtml(s.admin_notes || '') + '</textarea></div>' +
        '<div class="dash-card__actions">' +
        '<button type="button" class="btn btn--primary btn--sm" data-save-sitter="' + s.id + '">Save verification</button>' +
        '</div>' +
        '</div>'
      );
    }).join('');
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
  ];

  async function loadBookings() {
    bookingsList.innerHTML = '<div class="dash-empty">Loading bookings\u2026</div>';
    try {
      var data = await api.getAuth('/api/admin/bookings', headers());
      renderBookings(data.bookings || []);
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
      return (
        '<div class="dash-card" data-booking-card="' + b.id + '">' +
        '<div class="dash-card__head"><div><div class="dash-card__title">' + escapeHtml(b.parent_name) + ' &middot; ' + escapeHtml(b.booking_ref) + '</div>' +
        '<div class="dash-card__meta">' + fmtDate(b.booking_date) + ' at ' + escapeHtml(b.start_time) + ' &middot; ' + escapeHtml(b.duration_hours) + 'h &middot; Level ' + escapeHtml(b.level) + '</div></div>' + respBadge + '</div>' +
        '<dl class="dash-kv">' +
        '<div><dt>Phone</dt><dd>' + escapeHtml(b.phone) + '</dd></div>' +
        '<div><dt>Address</dt><dd>' + escapeHtml(b.address) + '</dd></div>' +
        '<div><dt>Children</dt><dd>' + escapeHtml(b.children_count) + '</dd></div>' +
        '</dl>' +
        '<div class="dash-checklist">' + checklist + '</div>' +
        '<div class="dash-docs">' + docLink('id_document', b.id, b.has_id_document, 'bookings', 'ID / passport document') + docLink('proof_of_address', b.id, b.has_proof_of_address, 'bookings', 'Proof of address') + '</div>' +
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
})();
