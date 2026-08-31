(function () {
  'use strict';
  var form = document.getElementById('sitter-form');
  if (!form) return;
  var submitBtn = document.getElementById('sitter-submit');
  var successBox = document.getElementById('sitter-success');
  var errorBox = document.getElementById('sitter-error');
  var errorText = document.getElementById('sitter-error-text');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    successBox.hidden = true;
    errorBox.hidden = true;

    if (!form.reportValidity()) return;

    var level = form.querySelector('input[name="experience_level"]:checked');
    if (!level) {
      errorText.textContent = 'Please select your experience level.';
      errorBox.hidden = false;
      return;
    }

    var payload = {
      full_name: form.full_name.value.trim(),
      id_number: form.id_number.value.trim(),
      phone: form.phone.value.trim(),
      email: form.email.value.trim(),
      address: form.address.value.trim(),
      experience_level: level.value,
      years_experience: form.years_experience.value.trim(),
      certifications: form.certifications.value.trim(),
      references_text: form.references_text.value.trim(),
      availability: form.availability.value.trim(),
      bank_name: form.bank_name.value.trim(),
      account_holder: form.account_holder.value.trim(),
      account_number: form.account_number.value.trim(),
      agreed_terms: form.agreed_terms.checked,
    };

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    try {
      await window.ETL_API.post('/api/register-sitter', payload);
      successBox.hidden = false;
      form.reset();
      successBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (err) {
      errorText.textContent = err.message || 'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit application';
    }
  });
})();
