// Google Analytics
(function() {
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-778929FT8G';
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', 'G-778929FT8G');

    // ── Conversion & CTA event tracking ──────────────────────────────────────

    // ── Carrying identity across to Stripe ───────────────────────────────────
    //
    // Revenue is reported from stripe-webhook.js, because that is the only
    // place that knows what was actually bought and for how much. A server
    // event has to name a user, though, and GA4 identifies users by the
    // client id held in the browser's _ga cookie — which Stripe's own pages
    // never see.
    //
    // Stripe passes client_reference_id from a payment-link URL straight
    // through to the checkout session, so the id travels as a query
    // parameter: site -> Stripe -> webhook -> GA4. The purchase then joins
    // the same user and the same session that the click came from, so the
    // acquisition source survives.
    //
    // Stripe restricts the value to alphanumerics, dashes and underscores,
    // and a GA4 client id is two integers joined by a dot, so the dot travels
    // as a dash. Stripe silently drops a value it considers invalid rather
    // than rejecting the payment, so a malformed id can cost attribution but
    // can never cost a sale.
    // https://docs.stripe.com/payment-links/url-parameters
    function ga4ClientId() {
        var m = /(?:^|;\s*)_ga=GA\d+\.\d+\.(\d+\.\d+)/.exec(document.cookie || '');
        return m ? m[1] : '';
    }

    function withClientRef(url) {
        if (url.indexOf('client_reference_id=') !== -1) return url;  // already stamped
        var cid = ga4ClientId();
        if (!cid) return url;          // no cookie: leave the link exactly as authored
        return url + (url.indexOf('?') === -1 ? '?' : '&') +
               'client_reference_id=ga-' + cid.replace('.', '-');
    }

    // Click tracking via event delegation — catches all CTAs across every page
    document.addEventListener('click', function(e) {
        var el = e.target.closest('a, button');
        if (!el) return;
        var href = el.getAttribute('href') || '';
        var text = (el.textContent || '').trim().substring(0, 60);
        var page = window.location.pathname;

        // Which host this link actually points at. Compared as a parsed
        // hostname rather than by substring on purpose: `indexOf` would read
        // https://buy.stripe.com.example.test/ — or any URL that merely
        // mentions the string in its path or query — as Stripe, and the
        // stamping below would hand that host the visitor's GA4 client id.
        // Non-http schemes (tel:, mailto:) yield '' and fall through to their
        // own branches further down, which match on href as before.
        var host = '';
        if (href) {
            try { host = new URL(href, window.location.href).hostname; }
            catch (e) { host = ''; }
        }

        // Stamp the GA4 client id onto any link that hands the visitor to
        // Stripe, so the server-side purchase event can find its way back to
        // this user. Done before the event below, so `href` is the URL the
        // browser will actually open.
        if (host === 'buy.stripe.com' || host === 'book.stripe.com') {
            var stamped = withClientRef(href);
            if (stamped !== href) {
                el.setAttribute('href', stamped);
                href = stamped;
            }
        }

        // PRIMARY CONVERSION: the $67 course checkout. Only book.stripe.com
        // was tracked before, so every click on the course's own buy button
        // was missing from the funnel.
        if (host === 'buy.stripe.com') {
            gtag('event', 'checkout_click', {
                event_category: 'conversion',
                event_label: text,
                page_location: page
            });
            return;
        }

        // PRIMARY CONVERSION: Stripe booking link click
        if (host === 'book.stripe.com') {
            gtag('event', 'booking_click', {
                event_category: 'conversion',
                event_label: text,
                page_location: page
            });
            return;
        }

        // Clicks to the Profit Leak Snapshot landing page
        if (href.indexOf('profit-leak-snapshot') !== -1) {
            gtag('event', 'snapshot_cta_click', {
                event_category: 'cta',
                event_label: text,
                page_location: page
            });
            return;
        }

        // Advisory page CTA clicks
        if (href.indexOf('advisory') !== -1 && el.className && el.className.indexOf('cta') !== -1) {
            gtag('event', 'advisory_cta_click', {
                event_category: 'cta',
                event_label: text,
                page_location: page
            });
            return;
        }

        // Phone clicks. The tel: link sits in the footer of every page and
        // produced no measurable data at all before this.
        if (href.indexOf('tel:') === 0) {
            gtag('event', 'phone_click', {
                event_category: 'conversion',
                event_label: page,
                page_location: page
            });
            return;
        }

        // Email clicks.
        if (href.indexOf('mailto:') === 0) {
            gtag('event', 'email_click', {
                event_category: 'conversion',
                event_label: page,
                page_location: page
            });
        }
    });

    // ── Form submissions ─────────────────────────────────────────────────────
    // Previously every form on the site fired one generic `form_submit`, so a
    // newsletter signup and a $350 consultation request were indistinguishable
    // in reporting. Each form now reports its own event name.
    var FORM_EVENTS = {
        contactForm:      'contact_form_submit',      // the $350 Snapshot enquiry
        'newsletter-form': 'newsletter_signup',
        leadCaptureForm:  'playbook_download',
        'login-form':     'account_login',
        'register-form':  'account_register',
        'forgot-form':    'account_password_reset',
        'reset-form':     'account_password_reset'
    };

    document.addEventListener('submit', function(e) {
        var form = e.target;
        var id = form.id || form.getAttribute('name') || '';
        var name = FORM_EVENTS[id] || 'form_submit';

        gtag('event', name, {
            event_category: name === 'contact_form_submit' ? 'conversion' : 'engagement',
            event_label: id || window.location.pathname,
            form_id: id,
            page_location: window.location.pathname
        });
    });

    // ── Exit-intent popup ────────────────────────────────────────────────────
    // The popup runs an A/B test between two lead magnets. Without these events
    // the variant cannot be read, so the test was decorative.
    window.treTrackExitIntent = function(action, variant) {
        gtag('event', 'exit_intent_' + action, {
            event_category: 'cta',
            event_label: variant || 'unknown',
            variant: variant || 'unknown',
            page_location: window.location.pathname
        });
    };

    // ── Reaching the thank-you page ──────────────────────────────────────────
    //
    // This deliberately does NOT send `purchase`. That event is sent once,
    // from stripe-webhook.js, and sending it from here as well would double
    // count: GA4 collapses two purchases that share a transaction id only
    // when they also share a user, and a buyer who opened the payment link
    // from an email carries no client id for the server to match. The
    // failure would be silent and would inflate revenue, so the browser
    // stays out of revenue entirely.
    //
    // What the browser still knows, and the server does not, is whether the
    // buyer ever arrived back on the site. Stripe returns to /success, which
    // netlify.toml:23-26 rewrites to thank-you.html while leaving the URL as
    // /success. A buyer who closes the tab at Stripe is paid up but never
    // onboarded, and that gap is worth being able to see.
    //
    // Only the $67 course comes back here — thank-you.html is written for it
    // by name. The $350 Snapshot goes to a book.stripe.com link
    // (profit-leak-snapshot.html:488) and finishes on Stripe's own page, so
    // it is invisible to this file and reaches GA4 only via the webhook.
    //
    // Fired once per browser session, keyed on the Stripe session id when
    // Stripe supplies one, so a refresh or a bookmark does not count again.
    function trackThankYouView() {
        var path = window.location.pathname;
        if (path.indexOf('/success') === -1 && path.indexOf('thank-you') === -1) return;

        var params = new URLSearchParams(window.location.search);
        var sessionId = params.get('session_id') || params.get('checkout_session_id');
        var key = 'thank_you_seen:' + (sessionId || path);

        try {
            if (window.sessionStorage.getItem(key)) return;   // already counted
            window.sessionStorage.setItem(key, '1');
        } catch (e) {
            // Private mode or blocked storage: better to count a refresh
            // twice than to lose the signal entirely. Nothing here carries
            // revenue, so a double count costs nothing but a view.
        }

        var payload = { event_category: 'engagement' };
        if (sessionId) payload.transaction_id = sessionId;
        gtag('event', 'course_thank_you_view', payload);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trackThankYouView);
    } else {
        trackThankYouView();
    }

})();
