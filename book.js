(function () {
  'use strict';
  var form = document.getElementById('booking-form');
  if (!form) return;

  var NATIONAL_MINIMUM_WAGE = 30.23;
  var RATE_BANDS = {
    '1|day': { min: 35, max: 45, commission: function () { return 0.10; } },
    '2|day': { min: 45, max: 65, commission: function () { return 0.125; } },
    '3|day': {
      min: 65,
      max: 85,
      commission: function (r) {
        var t = Math.max(0, Math.min(1, (r - 65) / 20));
        return 0.125 + 0.025 * t;
      },
    },
    '3|overnight': { min: 70, max: 80, commission: function () { return 0.125; } },
    '4|overnight': { min: 90, max: 100, commission: function () { return 0.125; } },
  };
  var MIN_HOURS = { day: 4, overnight: 10 };

  var bandHint = document.getElementById('band-hint');
  var levelSel = document.getElementById('level');
  var rateInput = document.getElementById('hourly_rate');
  var durationInput = document.getElementById('duration_hours');
  var quoteBox = document.getElementById('quote-box');
  var qRate = document.getElementById('q-rate');
  var qDuration = document.getElementById('q-duration');
  var qCommPct = document.getElementById('q-comm-pct');
  var qComm = document.getElementById('q-comm');
  var qFee = document.getElementById('q-fee');
  var qNet = document.getElementById('q-net');
  var qNote = document.getElementById('q-note');

  function rateType() {
    var el = form.querySelector('input[name="rate_type"]:checked');
    return el ? el.value : 'day';
  }

  function fmtR(n) {
    return 'R' + n.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function bandLabel(level, type) {
    var band = RATE_BANDS[level + '|' + type];
    if (!band) return 'This level does not support ' + type + ' bookings.';
    return 'Level ' + level + ' ' + type + ' band: R' + band.min + '\u2013R' + band.max + '/hour';
  }

  function updateHint() {
    bandHint.textContent = bandLabel(levelSel.value, rateType());
  }

  function updateLevelOptions() {
    var type = rateType();
    Array.prototype.forEach.call(levelSel.options, function (opt) {
      var ok = !!RATE_BANDS[opt.value + '|' + type];
      opt.disabled = !ok;
    });
    var current = levelSel.options[levelSel.selectedIndex];
    if (current.disabled) {
      for (var i = 0; i < levelSel.options.length; i++) {
        if (!levelSel.options[i].disabled) {
          levelSel.selectedIndex = i;
          break;
        }
      }
    }
    updateHint();
  }

  function recalcQuote() {
    var level = levelSel.value;
    var type = rateType();
    var rate = parseFloat(rateInput.value);
    var duration = parseFloat(durationInput.value);
    var band = RATE_BANDS[level + '|' + type];

    if (!band || isNaN(rate) || isNaN(duration) || rate <= 0 || duration <= 0) {
      quoteBox.hidden = true;
      return;
    }

    var minHours = MIN_HOURS[type];
    var applied = rate;
    var note = '';
    if (rate < NATIONAL_MINIMUM_WAGE || rate < band.min) {
      applied = Math.max(band.min, NATIONAL_MINIMUM_WAGE);
      note = 'Your rate is below the Level ' + level + ' ' + type + ' minimum or the National Minimum Wage (' + fmtR(NATIONAL_MINIMUM_WAGE) + '/hour) \u2014 automatically corrected to ' + fmtR(applied) + '/hour per Appendix C.';
    } else if (rate > band.max) {
      note = 'Your rate is above the Level ' + level + ' band ceiling (' + fmtR(band.max) + '/hour) \u2014 allowed, since only the floor is enforced.';
    }
    if (duration < minHours) {
      note = (note ? note + ' ' : '') + 'Minimum booking length for a ' + type + ' booking is ' + minHours + ' hours \u2014 your request will be rejected until duration is increased.';
    }

    var commRate = band.commission(applied);
    var fee = Math.round(applied * duration * 100) / 100;
    var comm = Math.round(fee * commRate * 100) / 100;
    var net = Math.round((fee - comm) * 100) / 100;

    qRate.textContent = fmtR(applied) + '/hr';
    qDuration.textContent = duration + ' hours';
    qCommPct.textContent = (commRate * 100).toFixed(1).replace(/\.0$/, '') + '%';
    qComm.textContent = fmtR(comm);
    qFee.textContent = fmtR(fee);
    qNet.textContent = fmtR(net);
    if (note) {
      qNote.textContent = note;
      qNote.hidden = false;
    } else {
      qNote.hidden = true;
    }
    quoteBox.hidden = false;
  }

  form.querySelectorAll('input[name="rate_type"]').forEach(function (el) {
    el.addEventListener('change', function () {
      updateLevelOptions();
      recalcQuote();
    });
  });
  levelSel.addEventListener('change', function () {
    updateHint();
    recalcQuote();
  });
  rateInput.addEventListener('input', recalcQuote);
  durationInput.addEventListener('input', recalcQuote);
  updateLevelOptions();

  var submitBtn = document.getElementById('booking-submit');
  var errorBox = document.getElementById('booking-error');
  var errorText = document.getElementById('booking-error-text');
  var resultBox = document.getElementById('booking-result');
  var resultRef = document.getElementById('result-ref');
  var resultPin = document.getElementById('result-pin');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    errorBox.hidden = true;
    if (!form.reportValidity()) return;

    var payload = {
      parent_name: form.parent_name.value.trim(),
      id_number: form.id_number.value.trim(),
      phone: form.phone.value.trim(),
      email: form.email.value.trim(),
      address: form.address.value.trim(),
      children_count: form.children_count.value.trim(),
      booking_date: form.booking_date.value,
      start_time: form.start_time.value,
      rate_type: rateType(),
      level: levelSel.value,
      hourly_rate: parseFloat(rateInput.value),
      duration_hours: parseFloat(durationInput.value),
      special_instructions: form.special_instructions.value.trim(),
      agreed_terms: form.agreed_terms.checked,
    };

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    try {
      var res = await window.ETL_API.post('/api/bookings', payload);
      resultRef.textContent = res.booking_ref;
      resultPin.textContent = res.pin;
      form.hidden = true;
      resultBox.hidden = false;
      resultBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (err) {
      errorText.textContent = err.message || 'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit booking request';
    }
  });
})();
