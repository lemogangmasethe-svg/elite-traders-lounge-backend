(function () {
  'use strict';
  var form = document.getElementById('sitter-form');
  if (!form) return;
  var submitBtn = document.getElementById('sitter-submit');
  var successBox = document.getElementById('sitter-success');
  var successText = document.getElementById('sitter-success-text');
  var contractLink = document.getElementById('sitter-contract-link');
  var accessBox = document.getElementById('sitter-access-box');
  var accessCodeEl = document.getElementById('sitter-access-code');
  var accessHint = document.getElementById('sitter-access-hint');
  var errorBox = document.getElementById('sitter-error');
  var errorText = document.getElementById('sitter-error-text');

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
  var policeClearanceInput = setupFileField('police_clearance_document');
  var childProtectionClearanceInput = setupFileField('child_protection_clearance_document');
  var foreignPoliceClearanceInput = setupFileField('foreign_police_clearance_document');
  var selfieCapture = window.ETLSelfieCapture && window.ETLSelfieCapture.attach('selfie');

  var DOCUMENT_LABELS = {
    id_document: 'ID/passport document',
    proof_of_address: 'proof of address document',
    police_clearance: 'AFIS check or police clearance certificate',
    child_protection_clearance: 'Child Protection Register (Part B) clearance letter',
    foreign_police_clearance: 'foreign police clearance certificate',
  };

  async function buildDocumentFields(prefix, input) {
    var label = DOCUMENT_LABELS[prefix] || prefix;
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

  // ID type toggle: show/hide SA ID vs Passport+work permit field groups
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
          if (input.id === 'id_number' || input.id === 'passport_number' || input.id === 'work_permit_number' || input.id === 'work_permit_expiry' || input.id === 'foreign_police_clearance_document') {
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

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    successBox.hidden = true;
    errorBox.hidden = true;
    if (contractLink) contractLink.hidden = true;

    if (!form.reportValidity()) return;

    var level = form.querySelector('input[name="experience_level"]:checked');
    if (!level) {
      errorText.textContent = 'Please select your experience level.';
      errorBox.hidden = false;
      return;
    }

    var idTypeChecked = form.querySelector('[data-id-type-toggle]:checked');
    var idType = idTypeChecked ? idTypeChecked.value : 'sa_id';

    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading documents...';
    try {
      var selfieFields = selfieCapture ? selfieCapture.buildFields() : (function () { throw new Error('Please capture a selfie using your camera before submitting.'); })();
      var idDocFields = await buildDocumentFields('id_document', idDocumentInput);
      var proofFields = await buildDocumentFields('proof_of_address', proofOfAddressDocInput);
      var policeClearanceFields = await buildDocumentFields('police_clearance', policeClearanceInput);
      var childProtectionClearanceFields = await buildDocumentFields('child_protection_clearance', childProtectionClearanceInput);
      var foreignPoliceClearanceFields = idType === 'passport'
        ? await buildDocumentFields('foreign_police_clearance', foreignPoliceClearanceInput)
        : {};

      var payload = Object.assign({
        full_name: form.full_name.value.trim(),
        id_type: idType,
        id_number: form.id_number.value.trim(),
        passport_number: form.passport_number.value.trim(),
        nationality: form.nationality.value.trim(),
        work_permit_number: form.work_permit_number.value.trim(),
        work_permit_expiry: form.work_permit_expiry.value.trim(),
        phone: form.phone.value.trim(),
        email: form.email.value.trim(),
        address: form.address.value.trim(),
        proof_of_address_type: form.proof_of_address_type.value,
        proof_of_address_confirmed: form.proof_of_address_confirmed.checked,
        smile_id_consent: form.smile_id_consent.checked,
        experience_level: level.value,
        years_experience: form.years_experience.value.trim(),
        certifications: form.certifications.value.trim(),
        reference_name: form.reference_name.value.trim(),
        reference_relationship: form.reference_relationship.value.trim(),
        reference_phone: form.reference_phone.value.trim(),
        reference_email: form.reference_email.value.trim(),
        reference_affidavit_consent: form.reference_affidavit_consent.checked,
        availability: form.availability.value.trim(),
        profile_gender: form.profile_gender.value,
        profile_race: form.profile_race.value,
        profile_age: parseInt(form.profile_age.value, 10) || 0,
        paystack_email: form.paystack_email.value.trim(),
        agreed_terms: form.agreed_terms.checked,
      }, idDocFields, proofFields, policeClearanceFields, childProtectionClearanceFields, foreignPoliceClearanceFields, selfieFields);

      submitBtn.textContent = 'Submitting...';
      var result = await window.ETL_API.post('/api/register-sitter', payload);
      if (successText) {
        successText.textContent = result && result.message
          ? result.message
          : 'Application received. Our team will contact you to complete Smile ID verification before you can accept bookings.';
      }
      if (contractLink && result && result.contract_url) {
        contractLink.href = API_ORIGIN + result.contract_url;
        contractLink.hidden = false;
        contractLink.textContent = result.contract_emailed
          ? 'Download your contract (also emailed to you)'
          : 'Download your contract';
      }
      if (accessCodeEl && result && result.access_code) {
        accessCodeEl.textContent = result.access_code;
        if (accessBox) accessBox.hidden = false;
        if (accessHint) accessHint.hidden = false;
      }
      successBox.hidden = false;
      form.reset();
      syncIdTypeFields();
      if (selfieCapture) selfieCapture.reset();
      ['id_document-status', 'proof_of_address_document-status', 'police_clearance_document-status', 'child_protection_clearance_document-status', 'foreign_police_clearance_document-status'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) { el.textContent = ''; el.className = 'file-status'; }
      });
      successBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    } catch (err) {
      errorText.textContent = err.message || 'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit application';
    }
  });
})();
