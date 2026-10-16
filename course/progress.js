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

  /**
   * The lesson-id scheme comes from the server, not from a copy of the
   * registry kept here. These are only the shape of an empty answer; every
   * field is replaced by what the GET returns before anything is rendered.
   */
  var scheme = { prefix: '', modules: 5, lessonsPerModule: 4, bonusIds: ['bonus'] };

  /** Which page are we on? Module pages carry their number in the filename. */
  function pageContext() {
    var path = (window.location.pathname || '').toLowerCase();
    // Which course: the only thing the browser works out for itself, because
    // it has to ask the server about one before the server can answer.
    var course = path.indexOf('/course/people/') === 0 ? 'catering-people' : 'catering-profit';
    var m = /module-([1-5])(?:\.html)?$/.exec(path);
    if (m) return { kind: 'module', module: parseInt(m[1], 10), course: course };
    if (/bonus(?:\.html)?$/.test(path)) return { kind: 'bonus', course: course };
    if (/dashboard(?:\.html)?$/.test(path)) return { kind: 'dashboard', course: course };
    return { kind: 'other', course: course };
  }

  /** The id for a lesson, built from whatever scheme the server sent. */
  function lessonId(moduleNo, lessonNo) {
    return scheme.prefix + 'm' + moduleNo + 'l' + lessonNo;
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

  function request(method, body, course) {
    var t = token();
    if (!t) return Promise.reject(new Error('no token'));
    var url = ENDPOINT + (course ? '?course=' + encodeURIComponent(course) : '');
    return fetch(url, {
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
      el.dataset.lessonId = lessonId(moduleNo, i + 1);
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
      var id = lessonId(ctx.module, i + 1);
      li.classList.toggle('is-done', completed.indexOf(id) !== -1);
    });
  }

  /**
   * A bonus page can hold more than one bonus lesson — the People course has
   * two — so each .lesson-video gets its own tick, matched to the bonus ids
   * in page order. Falling back to one tick at the top keeps a page that has
   * no .lesson-video blocks working as it did.
   */
  function renderBonus(completed) {
    var main = document.querySelector('.main-content') || document.querySelector('main');
    if (!main) return;
    var ids = scheme.bonusIds || [];
    var lessons = [].slice.call(document.querySelectorAll('.lesson-video'));

    if (lessons.length) {
      lessons.forEach(function (el, i) {
        var id = ids[i];
        if (!id) return;
        el.dataset.lessonId = id;
        el.appendChild(tick(id, completed.indexOf(id) !== -1, function (lessonId, next) {
          var at = completed.indexOf(lessonId);
          if (next && at === -1) completed.push(lessonId);
          if (!next && at !== -1) completed.splice(at, 1);
        }));
      });
      return;
    }

    var wrap = document.createElement('div');
    wrap.className = 'lg-progress';
    ids.forEach(function (id) {
      wrap.appendChild(tick(id, completed.indexOf(id) !== -1, function () {}));
    });
    main.insertBefore(wrap, main.firstChild);
  }

  function renderDashboard(completed, total) {
    var welcome = document.querySelector('.welcome-section');
    if (welcome) welcome.appendChild(meter(completed.length, total, 'lessons complete'));

    // Per-module counts on the cards, in the order the modules appear.
    var cards = document.querySelectorAll('.modules-grid .module-card');
    [].forEach.call(cards, function (card, idx) {
      var moduleNo = idx + 1;
      if (moduleNo > scheme.modules) return;
      var n = 0;
      for (var l = 1; l <= scheme.lessonsPerModule; l += 1) {
        if (completed.indexOf(lessonId(moduleNo, l)) !== -1) n += 1;
      }
      var tag = document.createElement('div');
      tag.className = 'lg-module-count';
      tag.innerHTML = '<span class="lg-progress__done">' + n + '</span>' +
        '<span class="lg-progress__of"> / ' + scheme.lessonsPerModule + '</span>' +
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
      return request('GET', null, ctx.course).then(function (data) {
        var completed = Array.isArray(data.completed) ? data.completed : [];
        var total = typeof data.total === 'number' ? data.total : 0;
        // Adopt the server's scheme before anything builds an id with it.
        if (typeof data.prefix === 'string') scheme.prefix = data.prefix;
        if (typeof data.modules === 'number') scheme.modules = data.modules;
        if (typeof data.lessonsPerModule === 'number') scheme.lessonsPerModule = data.lessonsPerModule;
        if (Array.isArray(data.bonusIds)) scheme.bonusIds = data.bonusIds;
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
