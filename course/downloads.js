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

  /**
   * The auth module.
   *
   * auth.js declares `const CourseAuth`, and a top-level const is a global
   * LEXICAL binding -- it is never a property of window, even though the bare
   * name resolves fine from another classic script on the page.
   *
   * This file used to read `window.CourseAuth && CourseAuth.getToken()`. That
   * expression short-circuits on the undefined window property before it ever
   * reaches the working name, so `token` was always undefined, the "not
   * signed in" branch fired on EVERY click, and every download redirected to
   * the login page -- which, until it was taught to honour ?redirect=, sent
   * the student to the dashboard. No download request was ever made. It
   * looked like a broken gate; it was a scoping mistake.
   *
   * progress.js and upgrade.js already carried this note. This file is where
   * it was still missing.
   */
  function auth() {
    return typeof CourseAuth === 'undefined' ? null : CourseAuth;
  }

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
      const token = auth() && auth().getToken();
      if (!token) {
        window.location.href =
          '/login.html?redirect=' + encodeURIComponent(
            window.location.pathname + window.location.search + window.location.hash);
        return;
      }

      let response = await fetch(href, {
        headers: { Authorization: 'Bearer ' + token },
      });

      // A dead access token is the ordinary case here, not an edge one: the
      // page was rendered when the token was alive and the click can come an
      // hour later. Renew once and try again before sending anyone to the
      // login page.
      if (response.status === 401 && auth() && auth().refresh && await auth().refresh()) {
        response = await fetch(href, {
          headers: { Authorization: 'Bearer ' + auth().getToken() },
        });
      }

      if (response.status === 401) {
        // Dead and not renewable. Clear it before redirecting: login.html
        // honours ?redirect=, so a session left in storage sends the student
        // straight back here without ever asking them to sign in.
        if (auth() && auth().clearSession) auth().clearSession();
        window.location.href =
          '/login.html?redirect=' + encodeURIComponent(
            window.location.pathname + window.location.search + window.location.hash);
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
