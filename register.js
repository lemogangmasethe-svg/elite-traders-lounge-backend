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
          if (input.id === 'id_number' || input.id === 'passport_number' || input.id === 'nationality' || input.id === 'work_permit_number' || input.id === 'work_permit_expiry') {
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

    var payload = {
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
      paystack_email: form.paystack_email.value.trim(),
      agreed_terms: form.agreed_terms.checked,
    };

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    try {
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
