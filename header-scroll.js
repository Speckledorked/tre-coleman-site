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

  // Add scroll listener
  window.addEventListener('scroll', handleScroll);

  // Check initial position
  handleScroll();
})();
