/**
 * Authenticated course downloads.
 *
 * The course files are no longer static assets — /course/downloads/* is
 * rewritten to the course-download function, which requires the same Supabase
 * bearer token the rest of the course uses. An <a href> cannot send an
 * Authorization header, so every download link is intercepted here and
 * re-issued as a fetch, then handed to the browser as a blob.
 *
 * The markup is untouched: the links keep their real hrefs and their download
 * attribute, so they remain meaningful, and the only thing this adds is the
 * header. Pages carrying these links already require JavaScript — they do not
 * render at all until CourseAuth.verifySession() resolves — so nothing that
 * worked without it stops working.
 */

(function () {
  'use strict';

  function label(anchor) {
    const row = anchor.closest('li');
    const name = row && row.querySelector('span');
    return (name ? name.textContent : anchor.textContent).trim();
  }

  async function message(response) {
    try {
      const body = await response.json();
      if (body && body.error) return body.error;
    } catch (_) { /* not JSON; fall through to the generic message */ }
    return 'That download could not be started. Please try again.';
  }

  async function download(anchor) {
    const href = anchor.getAttribute('href');
    const original = anchor.innerHTML;
    anchor.setAttribute('aria-busy', 'true');
    anchor.innerHTML = 'Preparing…';

    try {
      const token = window.CourseAuth && CourseAuth.getToken();
      if (!token) {
        window.location.href =
          '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
        return;
      }

      const response = await fetch(href, {
        headers: { Authorization: 'Bearer ' + token },
      });

      if (response.status === 401) {
        window.location.href =
          '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
        return;
      }
      if (response.status === 403) {
        window.location.href = '/course/no-access.html';
        return;
      }
      if (!response.ok) {
        window.alert(await message(response));
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = href.split('/').pop() || label(anchor);
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Revoke on the next tick; revoking synchronously can cancel the save
      // in some browsers before it has read the blob.
      setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
    } catch (error) {
      console.error('Download failed:', error);
      window.alert('That download could not be started. Please try again.');
    } finally {
      anchor.removeAttribute('aria-busy');
      anchor.innerHTML = original;
    }
  }

  document.addEventListener('click', function (event) {
    const anchor = event.target.closest('a[href*="downloads/"][download]');
    if (!anchor) return;
    event.preventDefault();
    download(anchor);
  });
})();
