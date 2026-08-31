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

  /* ---------- How it works tabs ---------- */
  var tabs = document.querySelectorAll('.tab');
  var familyPanel = document.getElementById('panel-family');
  var sitterPanel = document.getElementById('panel-sitter');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) {
        t.setAttribute('aria-selected', 'false');
      });
      tab.setAttribute('aria-selected', 'true');
      var which = tab.getAttribute('data-tab');
      if (which === 'family') {
        familyPanel.hidden = false;
        sitterPanel.hidden = true;
      } else {
        familyPanel.hidden = true;
        sitterPanel.hidden = false;
      }
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
})();
