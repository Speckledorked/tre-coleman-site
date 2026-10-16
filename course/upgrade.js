/**
 * What a dashboard says about the course you are NOT currently in.
 *
 * Two cases, and the second was missing until someone who owned both courses
 * found there was no way to reach the second one:
 *
 *   own ONE  -> offer the other (see the upgrade note below)
 *   own BOTH -> link to the other, because otherwise the only route to it is
 *               typing the URL
 *
 * The gap was asymmetric and so easy to miss: the People dashboard already
 * linked back to the Profit one, so it only bit in the direction nobody
 * tested. Buying the second course made the site look like it had not
 * registered the purchase.
 *
 * There is no upgrade LINK anywhere, deliberately. The upgrade price grants
 * both courses, because one Stripe price cannot know which one the buyer is
 * missing, so a public $100 URL would be worth $297 to anyone who found it —
 * and a Stripe payment link cannot be gated on a previous purchase. Instead
 * this asks course-upgrade-checkout for a Checkout Session, which it only
 * issues after checking the caller's token and what they actually own. The
 * URL does not exist until that passes, so there is nothing to share.
 *
 * This is presentation only. Hiding the button is not a security control —
 * the function re-checks entitlement, and stripe-webhook.js checks again on
 * the way back in — it just avoids offering something that cannot be bought.
 */
(function () {
  'use strict';

  var ENDPOINT = '/.netlify/functions/course-upgrade-checkout';

  /**
   * The courses, client-side.
   *
   * This duplicates netlify/functions/lib/courses.js, which is normally the
   * thing to avoid -- course-progress.js takes its lesson scheme from the
   * server for exactly that reason. Here the browser needs a name and a path
   * before it has asked the server anything, so a copy is unavoidable.
   *
   * tools/check_courses.js asserts this map against the registry, so the two
   * cannot drift apart silently. A course added there and forgotten here
   * would otherwise become quietly unreachable -- which is the bug this map
   * was extended to fix.
   */
  var COURSES = {
    'catering-profit': {
      name: 'The Catering Profit System',
      dashboard: '/course/dashboard.html'
    },
    'catering-people': {
      name: 'The Catering People System',
      dashboard: '/course/people/dashboard.html'
    }
  };

  /** Which course's dashboard is this? */
  function current() {
    var path = (window.location.pathname || '').toLowerCase();
    return path.indexOf('/course/people/') === 0 ? 'catering-people' : 'catering-profit';
  }

  function token() {
    // auth.js declares `const CourseAuth`, and a top-level const is a global
    // binding but NOT a property of window, so window.CourseAuth is undefined
    // here even though the bare name resolves. Guard with typeof.
    try {
      if (typeof CourseAuth === 'undefined' || !CourseAuth.getToken) return '';
      return CourseAuth.getToken() || '';
    } catch (e) {
      return '';
    }
  }

  function held() {
    try {
      if (typeof CourseAuth === 'undefined' || !CourseAuth.getCourses) return [];
      return CourseAuth.getCourses() || [];
    } catch (e) {
      return [];
    }
  }

  function render(missingName) {
    var main = document.querySelector('.main-content') || document.querySelector('main');
    if (!main) return;

    var wrap = document.createElement('section');
    wrap.className = 'welcome-section';

    var h = document.createElement('h2');
    h.textContent = 'Add ' + missingName;

    var p = document.createElement('p');
    p.textContent = 'You own one half of The Complete Catering System: Profit + People. '
      + 'Add the other for $100 — the difference between what you paid and the bundle.';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'module-btn';
    btn.textContent = 'Add it for $100';

    var note = document.createElement('p');
    note.className = 'lg-note';

    btn.addEventListener('click', function () {
      btn.disabled = true;
      var original = btn.textContent;
      btn.textContent = 'Opening checkout…';
      note.textContent = '';

      fetch(ENDPOINT, { method: 'POST', headers: { Authorization: 'Bearer ' + token() } })
        .then(function (res) {
          return res.json().then(function (body) { return { ok: res.ok, body: body }; });
        })
        .then(function (r) {
          if (r.ok && r.body && r.body.url) {
            window.location.href = r.body.url;
            return;
          }
          // Say what went wrong rather than failing silently. A student who
          // presses a button that does nothing assumes the site is broken.
          note.textContent = (r.body && r.body.error)
            || 'Could not start checkout. Please try again.';
          btn.disabled = false;
          btn.textContent = original;
        })
        .catch(function () {
          note.textContent = 'Could not start checkout. Please try again.';
          btn.disabled = false;
          btn.textContent = original;
        });
    });

    wrap.appendChild(h);
    wrap.appendChild(p);
    wrap.appendChild(btn);
    wrap.appendChild(note);
    main.appendChild(wrap);
  }

  /**
   * Links to the other courses this account already holds.
   *
   * Rendered at the TOP of the dashboard, not the bottom: someone who owns
   * both arrives looking for the other one, and a link below five module
   * cards is a link they have to go hunting for.
   */
  function renderSwitch(owned) {
    var here = current();
    var others = owned.filter(function (slug) {
      return slug !== here && COURSES[slug];
    });
    if (!others.length) return;

    var main = document.querySelector('.main-content') || document.querySelector('main');
    if (!main) return;

    var wrap = document.createElement('section');
    wrap.className = 'welcome-section';

    var h = document.createElement('h2');
    h.textContent = others.length > 1 ? 'Your other courses' : 'Your other course';
    wrap.appendChild(h);

    others.forEach(function (slug) {
      var p = document.createElement('p');
      var a = document.createElement('a');
      a.href = COURSES[slug].dashboard;
      a.className = 'module-btn';
      a.textContent = 'Go to ' + COURSES[slug].name + ' \u2192';
      p.appendChild(a);
      wrap.appendChild(p);
    });

    main.insertBefore(wrap, main.firstChild);
  }

  window.CourseUpgrade = {
    init: function () {
      var owned = held();

      // More than one: they already own the other, so link it rather than
      // trying to sell them something they have.
      if (owned.length > 1) {
        renderSwitch(owned);
        return;
      }

      // Exactly one: offer the other. None: nothing to upgrade from.
      if (owned.length !== 1) return;
      var other = owned[0] === 'catering-profit' ? 'catering-people' : 'catering-profit';
      if (!COURSES[other]) return;
      render(COURSES[other].name);
    }
  };
}());
