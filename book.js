(function () {
  'use strict';
  var form = document.getElementById('booking-form');
  if (!form) return;

  var NATIONAL_MINIMUM_WAGE = 30.23;
  // Appendix C — fixed rates (no more negotiated band). Elite Traders
  // Lounge's TOTAL commission is always 20% of the babysitter's fee, split
  // between the Family (added to the bill) and the Babysitter (deducted
  // from payout) — the split differs by level but always sums to 20%.
  var RATE_CARD = {
    '1|day': { hourly: 45, flat: 315, minHours: 5, sitterPct: 0.10, familyPct: 0.10 },
    '2|day': { hourly: 55, flat: 385, minHours: 5, sitterPct: 0.12, familyPct: 0.08 },
    '3|day': { hourly: 65, flat: 450, minHours: 4, sitterPct: 0.125, familyPct: 0.075 },
    '3|overnight': { hourly: 70, flat: 700, minHours: 10, sitterPct: 0.10, familyPct: 0.10 },
    '4|overnight': { hourly: 85, flat: 850, minHours: 10, sitterPct: 0.10, familyPct: 0.10 },
  };
  var FULL_DAY_HOURS = 7;

  var API_ORIGIN = (window.ETL_API && window.ETL_API.base) || '';

  var MAX_DOCUMENT_BYTES = 6 * 1024 * 1024;
  var ALLOWED_DOCUMENT_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf'];

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

  function setupFileField(inputId) {
    var input = document.getElementById(inputId);
    var status = document.getElementById(inputId + '-status');
    if (!input) return null;
    if (status) {
      input.addEventListener('change', function () {
        var file = input.files && input.files[0];
        if (!file) { status.textContent = ''; status.className = 'file-status'; return; }
        if (ALLOWED_DOCUMENT_TYPES.indexOf(file.type) === -1) {
          status.textContent = 'Please choose a JPG, PNG, or PDF file.';
          status.className = 'file-status file-status--error';
          input.value = '';
          return;
        }
        if (file.size > MAX_DOCUMENT_BYTES) {
          status.textContent = 'That file is too large. Please keep it under 6MB.';
          status.className = 'file-status file-status--error';
          input.value = '';
          return;
        }
        status.textContent = file.name + ' selected';
        status.className = 'file-status file-status--ok';
      });
    }
    return input;
  }

  var idDocumentInput = setupFileField('id_document');
  var proofOfAddressDocInput = setupFileField('proof_of_address_document');
  var selfieCapture = window.ETLSelfieCapture && window.ETLSelfieCapture.attach('selfie');

  async function buildDocumentFields(prefix, input) {
    var file = input && input.files && input.files[0];
    if (!file) throw new Error('Please upload your ' + (prefix === 'id_document' ? 'ID/passport document' : 'proof of address document') + '.');
    if (ALLOWED_DOCUMENT_TYPES.indexOf(file.type) === -1) {
      throw new Error('Please upload your ' + (prefix === 'id_document' ? 'ID/passport' : 'proof of address') + ' as a JPG, PNG, or PDF file.');
    }
    if (file.size > MAX_DOCUMENT_BYTES) {
      throw new Error('Your ' + (prefix === 'id_document' ? 'ID/passport' : 'proof of address') + ' file is too large. Please keep it under 6MB.');
    }
    var data = await readFileAsBase64(file);
    var fields = {};
    fields[prefix + '_data'] = data;
    fields[prefix + '_filename'] = file.name;
    fields[prefix + '_mimetype'] = file.type;
    return fields;
  }

  // ID type toggle: show/hide SA ID vs Passport field groups
  var idTypeRadios = form.querySelectorAll('[data-id-type-toggle]');
  var idFieldGroups = form.querySelectorAll('[data-id-fields]');
  function syncIdTypeFields() {
    var checked = form.querySelector('[data-id-type-toggle]:checked');
    var activeType = checked ? checked.value : 'sa_id';
    idFieldGroups.forEach(function (group) {
      var isActive = group.getAttribute('data-id-fields') === activeType;
      group.hidden = !isActive;
      group.querySelectorAll('input').forEach(function (input) {
        if (isActive) {
          if (input.id === 'id_number' || input.id === 'passport_number' || input.id === 'nationality') {
            input.required = true;
          }
        } else {
          input.required = false;
        }
      });
    });
  }
  idTypeRadios.forEach(function (radio) {
    radio.addEventListener('change', syncIdTypeFields);
  });
  syncIdTypeFields();

  // Pet disclosure toggle: show/hide pet type field
  var hasPetsRadios = form.querySelectorAll('[data-has-pets-toggle]');
  var petTypeField = form.querySelector('[data-pet-type-field]');
  var petTypeInput = document.getElementById('pet_type');
  function syncPetTypeField() {
    var checked = form.querySelector('[data-has-pets-toggle]:checked');
    var hasPets = checked && checked.value === 'yes';
    if (petTypeField) petTypeField.hidden = !hasPets;
    if (petTypeInput) petTypeInput.required = hasPets;
  }
  hasPetsRadios.forEach(function (radio) {
    radio.addEventListener('change', syncPetTypeField);
  });
  syncPetTypeField();

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
  var qFamilyComm = document.getElementById('q-family-comm');
  var qFamilyTotal = document.getElementById('q-family-total');
  var qNet = document.getElementById('q-net');
  var qNote = document.getElementById('q-note');
  var dayRateField = document.getElementById('day-rate-field');
  var dayRateDisplay = document.getElementById('day-rate-display');
  var dayCountField = document.getElementById('day-count-field');
  var dayCountInput = document.getElementById('day_count');
  var qFamilyCommPct = document.getElementById('q-family-comm-pct');
  var qSitterCommPct = document.getElementById('q-sitter-comm-pct');
  var qTotalCommPct = document.getElementById('q-total-comm-pct');

  // Babysitter browse: fetch verified sitters and show live availability based on chosen date/time/duration
  var sitterBrowseList = document.getElementById('sitter-browse-list');
  var sitterBrowseEmpty = document.getElementById('sitter-browse-empty');
  var GENDER_LABELS = { female: 'Female', male: 'Male', prefer_not_to_say: 'Prefer not to say' };
  var RACE_LABELS = { black_african: 'Black African', coloured: 'Coloured', indian_asian: 'Indian / Asian', white: 'White', other: 'Other', prefer_not_to_say: 'Prefer not to say' };

  function renderSitterCard(sitter) {
    var label = document.createElement('label');
    label.className = 'sitter-card' + (sitter.available === false ? ' sitter-card--unavailable' : '');
    var details = [];
    if (sitter.profile_gender) details.push(GENDER_LABELS[sitter.profile_gender] || sitter.profile_gender);
    if (sitter.profile_age) details.push(sitter.profile_age + ' yrs');
    if (sitter.nationality) details.push(sitter.nationality);
    if (sitter.profile_race) details.push(RACE_LABELS[sitter.profile_race] || sitter.profile_race);
    if (sitter.town) details.push(sitter.town);
    var ratingHtml = sitter.rating ? ('<span class="sitter-card__rating">\u2605 ' + sitter.rating.toFixed(1) + '</span>') : '<span class="sitter-card__rating sitter-card__rating--none">Not yet rated</span>';
    var availHtml = sitter.available === false
      ? '<span class="badge-verified badge-verified--pending">Unavailable for this slot</span>'
      : '<span class="badge-verified">Available</span>';
    var distanceHtml = '';
    if (typeof sitter.distance_km === 'number') {
      distanceHtml = sitter.is_local
        ? '<span class="badge-verified">' + sitter.distance_km + 'km away \u00b7 Local</span>'
        : '<span class="badge-verified badge-verified--pending">' + sitter.distance_km + 'km away \u00b7 Outside 40km area</span>';
    }
    var photoHtml = sitter.has_photo
      ? '<img src="' + API_ORIGIN + sitter.photo_url + '" alt="' + sitter.full_name + '" class="sitter-card__photo" />'
      : '<div class="sitter-card__photo sitter-card__photo--placeholder">' + (sitter.full_name ? sitter.full_name.charAt(0) : '?') + '</div>';
    label.innerHTML =
      '<input type="radio" name="preferred_sitter_id" value="' + sitter.id + '"' + (sitter.available === false ? ' disabled' : '') + ' />' +
      photoHtml +
      '<div class="sitter-card__body">' +
        '<strong>' + sitter.full_name + '</strong>' +
        '<span class="sitter-card__meta">' + details.join(' \u00b7 ') + '</span>' +
        '<span class="sitter-card__badges">' + ratingHtml + ' ' + availHtml + ' ' + distanceHtml + '</span>' +
      '</div>';
    return label;
  }

  async function loadSitterBrowse() {
    if (!sitterBrowseList) return;
    try {
      var params = new URLSearchParams();
      if (form.booking_date.value) params.set('date', form.booking_date.value);
      if (form.start_time.value) params.set('start_time', form.start_time.value);
      if (durationInput.value) params.set('duration_hours', durationInput.value);
      if (form.town && form.town.value.trim()) params.set('town', form.town.value.trim());
      if (form.province && form.province.value.trim()) params.set('province', form.province.value.trim());
      var query = params.toString();
      var result = await window.ETL_API.get('/api/babysitters/public' + (query ? '?' + query : ''));
      var sitters = (result && result.babysitters) || [];
      sitterBrowseList.innerHTML = '';
      if (!sitters.length) {
        var empty = document.createElement('p');
        empty.className = 'sitter-browse__empty';
        empty.textContent = 'No verified babysitters are listed yet. Submit your booking and our team will assign one manually.';
        sitterBrowseList.appendChild(empty);
        return;
      }
      sitters.forEach(function (sitter) {
        sitterBrowseList.appendChild(renderSitterCard(sitter));
      });
    } catch (err) {
      if (sitterBrowseEmpty) {
        sitterBrowseEmpty.textContent = 'Could not load babysitters right now \u2014 you can still submit your booking without choosing one.';
        sitterBrowseList.innerHTML = '';
        sitterBrowseList.appendChild(sitterBrowseEmpty);
      }
    }
  }
  ['booking_date', 'start_time'].forEach(function (name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (el) el.addEventListener('change', loadSitterBrowse);
  });
  if (durationInput) durationInput.addEventListener('change', loadSitterBrowse);
  loadSitterBrowse();

  // Coverage check: families must be able to see, before or during booking,
  // whether a verified babysitter can actually reach their town within our
  // 40km local service area.
  var coverageResult = document.getElementById('coverage-result');
  var coverageTimer = null;
  function checkCoverage() {
    if (!coverageResult) return;
    var town = form.town ? form.town.value.trim() : '';
    var province = form.province ? form.province.value.trim() : '';
    if (!town) { coverageResult.hidden = true; return; }
    if (coverageTimer) clearTimeout(coverageTimer);
    coverageTimer = setTimeout(async function () {
      try {
        var params = new URLSearchParams({ town: town });
        if (province) params.set('province', province);
        var res = await window.ETL_API.get('/api/coverage-check?' + params.toString());
        coverageResult.hidden = false;
        if (res.covered) {
          coverageResult.className = 'alert alert--success';
          coverageResult.textContent = '\u2705 ' + res.message;
        } else {
          coverageResult.className = 'alert alert--warning';
          coverageResult.textContent = '\u26a0\ufe0f ' + res.message;
        }
      } catch (err) {
        coverageResult.hidden = true;
      }
      loadSitterBrowse();
    }, 500);
  }
  if (form.town) form.town.addEventListener('blur', checkCoverage);
  if (form.province) form.province.addEventListener('change', checkCoverage);


  function rateType() {
    var el = form.querySelector('input[name="rate_type"]:checked');
    return el ? el.value : 'day';
  }

  function fmtR(n) {
    return 'R' + n.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function bandLookupType(type) {
    return type === 'full_day' ? 'day' : type;
  }

  function bandLabel(level, type) {
    var band = RATE_CARD[level + '|' + bandLookupType(type)];
    if (!band) return 'This level does not support ' + (type === 'full_day' ? 'full-day' : type) + ' bookings.';
    if (type === 'full_day') {
      return 'Level ' + level + ' full-day flat rate: R' + band.flat + '/day (' + FULL_DAY_HOURS + ' hours)';
    }
    return 'Level ' + level + ' ' + type + ' rate: R' + band.hourly + '/hour (fixed, minimum ' + band.minHours + ' hours)';
  }

  function updateHint() {
    bandHint.textContent = bandLabel(levelSel.value, rateType());
  }

  function updateLevelOptions() {
    var type = rateType();
    Array.prototype.forEach.call(levelSel.options, function (opt) {
      var ok = !!RATE_CARD[opt.value + '|' + bandLookupType(type)];
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
    updateDayRateField();
  }

  function pct(n) {
    return (n * 100).toFixed(1).replace(/\.0$/, '') + '%';
  }

  function recalcQuote() {
    var level = levelSel.value;
    var type = rateType();
    var duration = parseFloat(durationInput.value);
    var band = RATE_CARD[level + '|' + bandLookupType(type)];

    if (!band || isNaN(duration) || duration <= 0) {
      quoteBox.hidden = true;
      return;
    }

    var note = '';
    var applied = Math.max(band.hourly, NATIONAL_MINIMUM_WAGE);
    if (band.hourly < NATIONAL_MINIMUM_WAGE) {
      note = 'Level ' + level + ' ' + type + ' rate was below the National Minimum Wage (' + fmtR(NATIONAL_MINIMUM_WAGE) + '/hour) \u2014 automatically corrected to ' + fmtR(applied) + '/hour.';
    }

    var fee;
    if (type === 'full_day') {
      if (duration < FULL_DAY_HOURS || duration % FULL_DAY_HOURS !== 0) {
        note = (note ? note + ' ' : '') + 'Full-day bookings are billed in ' + FULL_DAY_HOURS + '-hour blocks (1 day = ' + FULL_DAY_HOURS + ' hours, 2 days = ' + (FULL_DAY_HOURS * 2) + ' hours, etc.).';
      }
      var dayCount = duration / FULL_DAY_HOURS;
      fee = Math.round(band.flat * dayCount * 100) / 100;
    } else {
      if (duration < band.minHours) {
        note = (note ? note + ' ' : '') + 'Minimum booking length for a Level ' + level + ' ' + type + ' booking is ' + band.minHours + ' hours \u2014 your request will be rejected until duration is increased.';
      }
      fee = Math.round(applied * duration * 100) / 100;
    }

    // Two-sided commission: Elite Traders Lounge's TOTAL commission is
    // always 20% of the fee, split between the Family (added to the bill)
    // and the Babysitter (deducted from payout) — the split differs by
    // level but always sums to 20%.
    var familyComm = Math.round(fee * band.familyPct * 100) / 100;
    var familyTotal = Math.round((fee + familyComm) * 100) / 100;
    var sitterComm = Math.round(fee * band.sitterPct * 100) / 100;
    var net = Math.round((fee - sitterComm) * 100) / 100;

    qRate.textContent = type === 'full_day' ? fmtR(band.flat) + '/day' : fmtR(applied) + '/hr';
    qDuration.textContent = duration + ' hours' + (type === 'full_day' ? ' (' + (duration / FULL_DAY_HOURS) + ' day' + (duration / FULL_DAY_HOURS === 1 ? '' : 's') + ')' : '');
    if (qFamilyCommPct) qFamilyCommPct.textContent = pct(band.familyPct);
    if (qSitterCommPct) qSitterCommPct.textContent = pct(band.sitterPct);
    if (qTotalCommPct) qTotalCommPct.textContent = pct(band.familyPct + band.sitterPct);
    qComm.textContent = fmtR(sitterComm);
    qFee.textContent = fmtR(fee);
    if (qFamilyComm) qFamilyComm.textContent = fmtR(familyComm);
    if (qFamilyTotal) qFamilyTotal.textContent = fmtR(familyTotal);
    qNet.textContent = fmtR(net);
    if (note) {
      qNote.textContent = note;
      qNote.hidden = false;
    } else {
      qNote.hidden = true;
    }
    quoteBox.hidden = false;
  }

  function updateDayRateField() {
    var type = rateType();
    var isFullDay = type === 'full_day';
    if (dayRateField) dayRateField.hidden = !isFullDay;
    if (dayCountField) dayCountField.hidden = !isFullDay;
    var rateField = rateInput ? rateInput.closest('.field') : null;
    var durationField = durationInput ? durationInput.closest('.field') : null;
    if (rateField) rateField.hidden = isFullDay;
    if (durationField) durationField.hidden = isFullDay;
    if (rateInput) rateInput.required = !isFullDay;
    if (durationInput) durationInput.required = !isFullDay;
    if (!isFullDay) {
      applyFixedRate();
      return;
    }
    applyDayRateSelection();
  }

  // Rates are fixed per level/type now — there is nothing for the family to
  // choose. This just fills the (read-only) rate input and lets
  // recalcQuote() do the math.
  function applyFixedRate() {
    var level = levelSel.value;
    var type = rateType();
    var band = RATE_CARD[level + '|' + bandLookupType(type)];
    if (rateInput) rateInput.value = band ? band.hourly : '';
    recalcQuote();
  }

  function applyDayRateSelection() {
    var level = levelSel.value;
    var band = RATE_CARD[level + '|day'];
    var days = parseInt((dayCountInput && dayCountInput.value) || '1', 10);
    if (!days || days < 1) days = 1;
    if (dayCountInput) dayCountInput.value = days;
    if (dayRateDisplay) {
      dayRateDisplay.textContent = band
        ? 'Level ' + level + ' flat day rate: R' + band.flat + '/day (' + FULL_DAY_HOURS + ' hours)'
        : 'This level does not support full-day bookings.';
    }
    if (band) {
      rateInput.value = band.hourly;
      durationInput.value = days * FULL_DAY_HOURS;
    } else {
      rateInput.value = '';
      durationInput.value = '';
    }
    recalcQuote();
  }

  form.querySelectorAll('input[name="rate_type"]').forEach(function (el) {
    el.addEventListener('change', function () {
      updateLevelOptions();
      recalcQuote();
    });
  });
  levelSel.addEventListener('change', function () {
    updateHint();
    updateDayRateField();
  });
  durationInput.addEventListener('input', recalcQuote);
  if (dayCountInput) dayCountInput.addEventListener('input', applyDayRateSelection);
  updateLevelOptions();
  updateDayRateField();

  var submitBtn = document.getElementById('booking-submit');
  var errorBox = document.getElementById('booking-error');
  var errorText = document.getElementById('booking-error-text');
  var resultBox = document.getElementById('booking-result');
  var resultRef = document.getElementById('result-ref');
  var resultPin = document.getElementById('result-pin');
  var resultMessage = document.getElementById('result-message');
  var resultContractLink = document.getElementById('result-contract-link');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    errorBox.hidden = true;
    if (!form.reportValidity()) return;

    var idTypeChecked = form.querySelector('[data-id-type-toggle]:checked');
    var idType = idTypeChecked ? idTypeChecked.value : 'sa_id';

    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading documents...';
    try {
      var selfieFields = selfieCapture ? selfieCapture.buildFields() : (function () { throw new Error('Please capture a selfie using your camera before submitting.'); })();
      var idDocFields = await buildDocumentFields('id_document', idDocumentInput);
      var proofFields = await buildDocumentFields('proof_of_address', proofOfAddressDocInput);

      var payload = Object.assign({
        parent_name: form.parent_name.value.trim(),
        id_type: idType,
        id_number: form.id_number.value.trim(),
        passport_number: form.passport_number.value.trim(),
        nationality: form.nationality.value.trim(),
        phone: form.phone.value.trim(),
        email: form.email.value.trim(),
        address: form.address.value.trim(),
        town: form.town.value.trim(),
        province: form.province.value.trim(),
        children_count: form.children_count.value.trim(),
        proof_of_address_type: form.proof_of_address_type.value,
        proof_of_address_confirmed: form.proof_of_address_confirmed.checked,
        paystack_email: form.paystack_email.value.trim(),
        smile_id_consent: form.smile_id_consent.checked,
        booking_date: form.booking_date.value,
        start_time: form.start_time.value,
        rate_type: rateType(),
        level: levelSel.value,
        hourly_rate: parseFloat(rateInput.value),
        duration_hours: parseFloat(durationInput.value),
        special_instructions: form.special_instructions.value.trim(),
        has_pets: (form.querySelector('[data-has-pets-toggle]:checked') || {}).value === 'yes',
        pet_type: form.pet_type.value.trim(),
        special_bath_baby: form.special_bath_baby.checked,
        special_feed_baby: form.special_feed_baby.checked,
        special_precautions: form.special_precautions.value.trim(),
        preferred_sitter_id: (function () {
          var el = form.querySelector('input[name="preferred_sitter_id"]:checked');
          var v = el ? el.value : '';
          return v ? parseInt(v, 10) : null;
        })(),
        agreed_terms: form.agreed_terms.checked,
      }, idDocFields, proofFields, selfieFields);

      submitBtn.textContent = 'Submitting...';
      var res = await window.ETL_API.post('/api/bookings', payload);
      resultRef.textContent = res.booking_ref;
      resultPin.textContent = res.pin;
      if (resultMessage && res.message) {
        resultMessage.textContent = res.message;
      }
      if (resultContractLink && res.contract_url) {
        resultContractLink.href = API_ORIGIN + res.contract_url;
        resultContractLink.hidden = false;
        resultContractLink.textContent = res.contract_emailed
          ? 'Download Family Service Agreement (also emailed to you)'
          : 'Download Family Service Agreement';
      }
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
