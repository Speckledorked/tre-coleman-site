/**
 * Lesson progress UI for the Catering Profit System.
 *
 * Talks to /.netlify/functions/course-progress with the same Bearer token the
 * rest of the course uses. Every page that loads this already waits for
 * CourseAuth.verifySession() before rendering, so by the time this runs there
 * is a token or the page has already redirected to login.
 *
 * Progress is stored server-side per account rather than in localStorage,
 * because a student who watches module 1 on a laptop and module 2 on a phone
 * should see one course, not two. localStorage would also quietly reset on a
 * cleared cache and read as "nothing completed", which is worse than having
 * no tracker at all.
 *
 * If the endpoint is unreachable the controls are not rendered. A dead tick
 * box that silently fails to save is a worse experience than no tick box, and
 * it would also misreport progress as zero.
 */
(function () {
  'use strict';

  var ENDPOINT = '/.netlify/functions/course-progress';
  var LESSONS_PER_MODULE = 4;
  var MODULE_COUNT = 5;

  /** Which page are we on? Module pages carry their number in the filename. */
  function pageContext() {
    var path = (window.location.pathname || '').toLowerCase();
    var m = /module-([1-5])(?:\.html)?$/.exec(path);
    if (m) return { kind: 'module', module: parseInt(m[1], 10) };
    if (/bonus(?:\.html)?$/.test(path)) return { kind: 'bonus' };
    if (/dashboard(?:\.html)?$/.test(path)) return { kind: 'dashboard' };
    return { kind: 'other' };
  }

  /**
   * auth.js declares `const CourseAuth`, and a top-level const is a global
   * binding but NOT a property of window -- so `window.CourseAuth` is
   * undefined here even though the bare name resolves. Guard with typeof.
   */
  function token() {
    try {
      if (typeof CourseAuth === 'undefined' || !CourseAuth.getToken) return '';
      return CourseAuth.getToken() || '';
    } catch (e) {
      return '';
    }
  }

  function request(method, body) {
    var t = token();
    if (!t) return Promise.reject(new Error('no token'));
    return fetch(ENDPOINT, {
      method: method,
      headers: body
        ? { Authorization: 'Bearer ' + t, 'Content-Type': 'application/json' }
        : { Authorization: 'Bearer ' + t },
      body: body ? JSON.stringify(body) : undefined,
    }).then(function (res) {
      if (!res.ok) throw new Error('progress request failed: ' + res.status);
      return res.json();
    });
  }

  /* --- rendering ---------------------------------------------------------- */

  /**
   * A figure and a rule that fills: the count is the information, the rule is
   * the ledger line being drawn. Not a progress bar with a percentage inside
   * it -- the denominator matters more than the percentage here, because "3 of
   * 4" tells a student what is left and "75%" does not.
   */
  function meter(done, total, label) {
    var wrap = document.createElement('div');
    wrap.className = 'lg-progress';
    var pct = total ? Math.round((done / total) * 100) : 0;

    var figure = document.createElement('div');
    figure.className = 'lg-progress__figure';
    figure.innerHTML = '<span class="lg-progress__done">' + done + '</span>' +
      '<span class="lg-progress__of"> / ' + total + '</span> ' +
      '<span class="lg-progress__label">' + label + '</span>';

    var track = document.createElement('div');
    track.className = 'lg-progress__track';
    var fill = document.createElement('div');
    fill.className = 'lg-progress__fill';
    fill.style.width = pct + '%';
    track.appendChild(fill);

    wrap.appendChild(figure);
    wrap.appendChild(track);
    wrap.setAttribute('role', 'group');
    wrap.setAttribute('aria-label', done + ' of ' + total + ' ' + label.toLowerCase());
    return wrap;
  }

  function tick(lessonId, isDone, onToggle) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'lg-tick' + (isDone ? ' is-done' : '');
    btn.setAttribute('aria-pressed', isDone ? 'true' : 'false');
    btn.dataset.lesson = lessonId;
    btn.textContent = isDone ? 'Completed' : 'Mark complete';

    btn.addEventListener('click', function () {
      var next = btn.getAttribute('aria-pressed') !== 'true';
      btn.disabled = true;
      // Optimistic, but reverted on failure: a tick that appears to save and
      // did not is the one outcome worth ruling out.
      request('POST', { lesson_id: lessonId, completed: next })
        .then(function () {
          btn.classList.toggle('is-done', next);
          btn.setAttribute('aria-pressed', next ? 'true' : 'false');
          btn.textContent = next ? 'Completed' : 'Mark complete';
          onToggle(lessonId, next);
        })
        .catch(function (err) {
          console.error('progress: could not save', err);
          btn.textContent = 'Could not save — try again';
          setTimeout(function () {
            btn.textContent = btn.getAttribute('aria-pressed') === 'true'
              ? 'Completed' : 'Mark complete';
          }, 2500);
        })
        .then(function () { btn.disabled = false; });
    });
    return btn;
  }

  /* --- per page ----------------------------------------------------------- */

  function renderModule(moduleNo, completed) {
    var lessons = [].slice.call(document.querySelectorAll('.lesson-video'));
    if (!lessons.length) return;

    // Stamp the ids BEFORE the first meter is built: done() reads them, so
    // computing the meter first reported 0 of 4 on a module with lessons
    // already complete, while the ticks beneath it were correctly marked.
    lessons.forEach(function (el, i) {
      el.dataset.lessonId = 'm' + moduleNo + 'l' + (i + 1);
    });

    var done = function () {
      return lessons.filter(function (el) {
        return completed.indexOf(el.dataset.lessonId) !== -1;
      }).length;
    };

    var summary = meter(done(), lessons.length, 'lessons complete');
    var main = document.querySelector('.main-content');
    if (main) main.insertBefore(summary, main.firstChild);

    function refresh() {
      var fresh = meter(done(), lessons.length, 'lessons complete');
      if (summary.parentNode) {
        summary.parentNode.replaceChild(fresh, summary);
        summary = fresh;
      }
      markSidebar(completed);
    }

    lessons.forEach(function (el) {
      var id = el.dataset.lessonId;
      var isDone = completed.indexOf(id) !== -1;
      el.appendChild(tick(id, isDone, function (lessonId, next) {
        var at = completed.indexOf(lessonId);
        if (next && at === -1) completed.push(lessonId);
        if (!next && at !== -1) completed.splice(at, 1);
        refresh();
      }));
    });

    markSidebar(completed);
  }

  /** The sidebar list is the student's map of the module; mark it up to match. */
  function markSidebar(completed) {
    var items = document.querySelectorAll('.lessons-list li');
    var ctx = pageContext();
    if (ctx.kind !== 'module') return;
    [].forEach.call(items, function (li, i) {
      var id = 'm' + ctx.module + 'l' + (i + 1);
      li.classList.toggle('is-done', completed.indexOf(id) !== -1);
    });
  }

  function renderBonus(completed) {
    var main = document.querySelector('.main-content') || document.querySelector('main');
    if (!main) return;
    var wrap = document.createElement('div');
    wrap.className = 'lg-progress';
    wrap.appendChild(tick('bonus', completed.indexOf('bonus') !== -1, function () {}));
    main.insertBefore(wrap, main.firstChild);
  }

  function renderDashboard(completed, total) {
    var welcome = document.querySelector('.welcome-section');
    if (welcome) welcome.appendChild(meter(completed.length, total, 'lessons complete'));

    // Per-module counts on the cards, in the order the modules appear.
    var cards = document.querySelectorAll('.modules-grid .module-card');
    [].forEach.call(cards, function (card, idx) {
      var moduleNo = idx + 1;
      if (moduleNo > MODULE_COUNT) return;
      var n = 0;
      for (var l = 1; l <= LESSONS_PER_MODULE; l += 1) {
        if (completed.indexOf('m' + moduleNo + 'l' + l) !== -1) n += 1;
      }
      var tag = document.createElement('div');
      tag.className = 'lg-module-count';
      tag.innerHTML = '<span class="lg-progress__done">' + n + '</span>' +
        '<span class="lg-progress__of"> / ' + LESSONS_PER_MODULE + '</span>' +
        '<span class="lg-progress__label"> complete</span>';
      var header = card.querySelector('.module-header');
      if (header) header.appendChild(tag);
    });
  }

  /* --- boot --------------------------------------------------------------- */

  window.CourseProgress = {
    init: function () {
      var ctx = pageContext();
      if (ctx.kind === 'other') return Promise.resolve();
      return request('GET').then(function (data) {
        var completed = Array.isArray(data.completed) ? data.completed : [];
        var total = typeof data.total === 'number' ? data.total : 21;
        if (ctx.kind === 'module') renderModule(ctx.module, completed);
        else if (ctx.kind === 'bonus') renderBonus(completed);
        else if (ctx.kind === 'dashboard') renderDashboard(completed, total);
      }).catch(function (err) {
        // No controls rather than broken controls. See the file header.
        console.error('progress: unavailable', err);
      });
    },
  };
}());
