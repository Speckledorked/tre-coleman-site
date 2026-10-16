/**
 * The "add the other course" offer, shown on a dashboard to a student who
 * owns exactly one of the two courses.
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

  var OTHER = {
    'catering-profit': 'The Catering People System',
    'catering-people': 'The Catering Profit System'
  };

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

  window.CourseUpgrade = {
    init: function () {
      var owned = held();
      // Exactly one: nothing to upgrade from with none, nothing to add with
      // both.
      if (owned.length !== 1) return;
      var missing = OTHER[owned[0]];
      if (!missing) return;
      render(missing);
    }
  };
}());
