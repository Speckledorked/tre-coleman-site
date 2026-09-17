/**
 * Header Scroll Effect
 * Makes header transparent at top, solid navy on scroll
 */
(function() {
  const header = document.querySelector('header');
  if (!header) return;

  function handleScroll() {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  // Passive: this handler never calls preventDefault, and saying so lets the
  // browser keep scrolling on the compositor instead of waiting on JS.
  window.addEventListener('scroll', handleScroll, { passive: true });

  // Check initial position
  handleScroll();
})();
