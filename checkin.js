(function () {
  'use strict';
  var form = document.getElementById('checkin-form');
  if (!form) return;

  var roleButtons = document.querySelectorAll('.role-toggle button');
  var role = 'sitter';
  roleButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      role = btn.getAttribute('data-role');
      roleButtons.forEach(function (b) {
        b.setAttribute('aria-pressed', String(b === btn));
      });
    });
  });

  var submitBtn = document.getElementById('checkin-submit');
  var lookupBtn = document.getElementById('checkin-lookup');
  var successBox = document.getElementById('checkin-success');
  var successText = document.getElementById('checkin-success-text');
  var errorBox = document.getElementById('checkin-error');
  var errorText = document.getElementById('checkin-error-text');

  var statusEmpty = document.getElementById('status-empty');
  var statusContent = document.getElementById('status-content');
  var workedBanner = document.getElementById('worked-hours-banner');
  var workedValue = document.getElementById('worked-hours-value');

  function fmtTs(iso) {
    if (!iso) return '';
    try {
      var d = new Date(iso);
      return d.toLocaleString('en-ZA', { dateStyle: 'medium', timeStyle: 'short' });
    } catch (e) {
      return iso;
    }
  }

  function renderSummary(summary) {
    statusEmpty.hidden = true;
    statusContent.hidden = false;

    var rows = [
      ['sitter-arrival', summary.sitter_arrival],
      ['parent-arrival', summary.parent_arrival],
      ['sitter-departure', summary.sitter_departure],
      ['parent-departure', summary.parent_departure],
    ];
    rows.forEach(function (row) {
      var key = row[0];
      var ts = row[1];
      var pill = document.getElementById('pill-' + key);
      var tsEl = document.getElementById('ts-' + key);
      if (ts) {
        pill.textContent = 'Confirmed';
        pill.className = 'status-pill status-pill--done';
        tsEl.textContent = fmtTs(ts);
      } else {
        pill.textContent = 'Pending';
        pill.className = 'status-pill status-pill--pending';
        tsEl.textContent = '';
      }
    });

    if (summary.worked_hours != null) {
      workedValue.textContent = summary.worked_hours + ' hours';
      workedBanner.hidden = false;
    } else {
      workedBanner.hidden = true;
    }
  }

  async function lookup(ref, pin) {
    var data = await window.ETL_API.get('/api/bookings/' + encodeURIComponent(ref) + '?pin=' + encodeURIComponent(pin));
    renderSummary(data.summary);
    return data;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    successBox.hidden = true;
    errorBox.hidden = true;
    if (!form.reportValidity()) return;

    var ref = form.booking_ref.value.trim().toUpperCase();
    var pin = form.pin.value.trim();
    var action = form.querySelector('input[name="action"]:checked').value;
    var note = form.note.value.trim();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Confirming...';
    try {
      var res = await window.ETL_API.post('/api/checkin', {
        booking_ref: ref,
        pin: pin,
        role: role,
        action: action,
        note: note,
      });
      successText.textContent = (role === 'sitter' ? 'Babysitter' : 'Parent/guardian') + ' ' + action + ' confirmed at ' + fmtTs(res.timestamp) + '.';
      successBox.hidden = false;
      renderSummary(res.summary);
    } catch (err) {
      errorText.textContent = err.message || 'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Confirm now';
    }
  });

  lookupBtn.addEventListener('click', async function () {
    errorBox.hidden = true;
    successBox.hidden = true;
    var ref = form.booking_ref.value.trim().toUpperCase();
    var pin = form.pin.value.trim();
    if (!ref || !pin) {
      errorText.textContent = 'Enter the booking reference and PIN to look up status.';
      errorBox.hidden = false;
      return;
    }
    lookupBtn.disabled = true;
    lookupBtn.textContent = 'Looking up...';
    try {
      await lookup(ref, pin);
    } catch (err) {
      errorText.textContent = err.message || 'Booking not found.';
      errorBox.hidden = false;
    } finally {
      lookupBtn.disabled = false;
      lookupBtn.textContent = 'Look up booking status';
    }
  });
})();
