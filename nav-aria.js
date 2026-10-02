/**
 * Keeps the navigation's ARIA state in step with what is actually on screen.
 *
 * The menu and its dropdowns are opened by toggling an `active` class, and the
 * aria-expanded attributes beside them were static: the hamburger had none at
 * all, and the two dropdown toggles that had one reported "false" whether they
 * were open or shut. A screen reader was therefore told the opposite of what
 * a sighted user could see.
 *
 * This watches the class attribute rather than binding to clicks, because the
 * inline handlers come in two different shapes across the site (toggleMenu on
 * most pages, toggleMobileMenu on three) and a third would be another thing to
 * keep in step. Observing the result works for every variant, including a menu
 * closed by the overlay, by a link, or by a resize.
 *
 * Additive on purpose: it changes no existing handler and removes no
 * behaviour. If this file fails to load, the menu still works exactly as it
 * did — it is just silent to assistive technology again.
 */

(function () {
  'use strict';

  function sync(element, isOpen) {
    if (element) element.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  }

  function start() {
    const nav = document.getElementById('mainNav');
    const toggle = document.getElementById('mobileMenuToggle');

    if (nav && toggle) {
      if (!toggle.hasAttribute('aria-controls')) {
        toggle.setAttribute('aria-controls', 'mainNav');
      }
      sync(toggle, nav.classList.contains('active'));
      new MutationObserver(function () {
        sync(toggle, nav.classList.contains('active'));
      }).observe(nav, { attributes: true, attributeFilter: ['class'] });
    }

    document.querySelectorAll('.nav-dropdown').forEach(function (item) {
      // The first link is the toggle; the rest are inside the panel.
      const trigger = item.querySelector('a');
      if (!trigger) return;
      if (!trigger.hasAttribute('aria-haspopup')) {
        trigger.setAttribute('aria-haspopup', 'true');
      }
      sync(trigger, item.classList.contains('active'));
      new MutationObserver(function () {
        sync(trigger, item.classList.contains('active'));
      }).observe(item, { attributes: true, attributeFilter: ['class'] });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
