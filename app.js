(function () {
  'use strict';

  /* ---------- Theme toggle ---------- */
  var toggle = document.querySelector('[data-theme-toggle]');
  var root = document.documentElement;
  var theme = matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
  root.setAttribute('data-theme', theme);

  function setToggleIcon() {
    if (!toggle) return;
    toggle.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
    toggle.innerHTML =
      theme === 'dark'
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
  setToggleIcon();

  if (toggle) {
    toggle.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
      setToggleIcon();
    });
  }

  /* ---------- Mobile menu ---------- */
  var menuToggle = document.querySelector('[data-menu-toggle]');
  var mobileMenu = document.querySelector('[data-mobile-menu]');
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', function () {
      var open = mobileMenu.classList.toggle('is-open');
      menuToggle.setAttribute('aria-expanded', String(open));
    });
    mobileMenu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mobileMenu.classList.remove('is-open');
        menuToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- Tabs (How it works, guide, partners — any number of tabs per group) ---------- */
  document.querySelectorAll('.tabs').forEach(function (tabGroup) {
    var groupTabs = tabGroup.querySelectorAll('.tab');
    groupTabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        groupTabs.forEach(function (t) {
          t.setAttribute('aria-selected', 'false');
          var panel = document.getElementById(t.getAttribute('aria-controls'));
          if (panel) panel.hidden = true;
        });
        tab.setAttribute('aria-selected', 'true');
        var activePanel = document.getElementById(tab.getAttribute('aria-controls'));
        if (activePanel) activePanel.hidden = false;
      });
    });
  });

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var btn = item.querySelector('.faq-item__q');
    var answer = item.querySelector('.faq-item__a');
    btn.addEventListener('click', function () {
      var isOpen = item.getAttribute('data-open') === 'true';
      // close all
      document.querySelectorAll('.faq-item').forEach(function (i) {
        i.setAttribute('data-open', 'false');
        i.querySelector('.faq-item__q').setAttribute('aria-expanded', 'false');
        i.querySelector('.faq-item__a').style.maxHeight = null;
      });
      if (!isOpen) {
        item.setAttribute('data-open', 'true');
        btn.setAttribute('aria-expanded', 'true');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  /* ---------- Hotel / Airbnb partner inquiry form ---------- */
  var partnerForm = document.getElementById('partner-form');
  if (partnerForm && window.ETL_API) {
    var partnerSubmit = document.getElementById('partner-submit');
    var partnerError = document.getElementById('partner-error');
    var partnerErrorText = document.getElementById('partner-error-text');
    var partnerSuccess = document.getElementById('partner-success');

    partnerForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      partnerError.hidden = true;
      partnerSuccess.hidden = true;
      if (!partnerForm.reportValidity()) return;

      var payload = {
        business_name: partnerForm.business_name.value.trim(),
        property_type: partnerForm.property_type.value,
        contact_name: partnerForm.contact_name.value.trim(),
        email: partnerForm.email.value.trim(),
        phone: partnerForm.phone.value.trim(),
        city: partnerForm.city.value.trim(),
        message: partnerForm.message.value.trim(),
      };

      partnerSubmit.disabled = true;
      partnerSubmit.textContent = 'Sending...';
      try {
        await window.ETL_API.post('/api/partner-inquiries', payload);
        partnerForm.reset();
        partnerSuccess.hidden = false;
      } catch (err) {
        partnerErrorText.textContent = err.message || 'Something went wrong. Please try again, or email us directly.';
        partnerError.hidden = false;
      } finally {
        partnerSubmit.disabled = false;
        partnerSubmit.textContent = 'Send partnership inquiry';
      }
    });
  }

  /* ---------- Service area coverage check + live towns list ---------- */
  if (window.ETL_API) {
    var coverageTownInput = document.getElementById('coverage-town');
    var coverageCheckBtn = document.getElementById('coverage-check-btn');
    var homeCoverageResult = document.getElementById('home-coverage-result');
    var serviceAreasList = document.getElementById('service-areas-list');

    async function runCoverageCheck() {
      if (!coverageTownInput || !homeCoverageResult) return;
      var town = coverageTownInput.value.trim();
      if (!town) { homeCoverageResult.hidden = true; return; }
      homeCoverageResult.hidden = false;
      homeCoverageResult.className = 'alert alert--info';
      homeCoverageResult.textContent = 'Checking...';
      try {
        var res = await window.ETL_API.get('/api/coverage-check?town=' + encodeURIComponent(town));
        homeCoverageResult.className = 'alert ' + (res.covered ? 'alert--success' : 'alert--warning');
        homeCoverageResult.textContent = (res.covered ? '\u2705 ' : '\u26a0\ufe0f ') + res.message;
      } catch (err) {
        homeCoverageResult.className = 'alert alert--error';
        homeCoverageResult.textContent = 'Could not check coverage right now \u2014 please try again shortly.';
      }
    }
    if (coverageCheckBtn) coverageCheckBtn.addEventListener('click', runCoverageCheck);
    if (coverageTownInput) {
      coverageTownInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); runCoverageCheck(); }
      });
    }

    async function loadServiceAreas() {
      if (!serviceAreasList) return;
      try {
        var res = await window.ETL_API.get('/api/service-areas');
        var areas = (res && res.areas) || [];
        serviceAreasList.innerHTML = '';
        if (!areas.length) {
          serviceAreasList.innerHTML = '<p>We\'re onboarding our first verified babysitters now \u2014 check back soon, or register above to be matched as soon as a sitter joins near you.</p>';
          return;
        }
        areas.forEach(function (area) {
          var item = document.createElement('div');
          item.className = 'check-item';
          item.innerHTML =
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-6.5-7-11a7 7 0 0 1 14 0c0 4.5-7 11-7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>' +
            '<div><h3>' + area.town + (area.province ? ', ' + area.province : '') + '</h3>' +
            '<p>' + area.sitter_count + ' verified babysitter' + (area.sitter_count === 1 ? '' : 's') + ' within reach</p></div>';
          serviceAreasList.appendChild(item);
        });
      } catch (err) {
        serviceAreasList.innerHTML = '<p>Could not load current coverage right now.</p>';
      }
    }
    loadServiceAreas();
  }
})();
