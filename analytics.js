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

    // Click tracking via event delegation — catches all CTAs across every page
    document.addEventListener('click', function(e) {
        var el = e.target.closest('a, button');
        if (!el) return;
        var href = el.getAttribute('href') || '';
        var text = (el.textContent || '').trim().substring(0, 60);
        var page = window.location.pathname;

        // PRIMARY CONVERSION: Stripe booking link click
        if (href.indexOf('book.stripe.com') !== -1) {
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

    // ── Completed purchase ───────────────────────────────────────────────────
    //
    // booking_click fires when someone heads TO Stripe. Nothing fired when they
    // came back having paid, so GA4 could report how many people reached
    // checkout and nothing about how many bought — the one number the funnel
    // exists to produce.
    //
    // Stripe returns to /success, which netlify.toml rewrites to
    // thank-you.html while leaving the URL as /success.
    //
    // Two things make a page-based purchase event lie, and both are handled:
    // a refresh or a bookmarked page would count again, so the event is fired
    // once per browser session and keyed on the Stripe session id when Stripe
    // supplies one.
    //
    // What this deliberately does NOT send is `value`. Both products land on
    // this same page and the page cannot tell which was bought, so any figure
    // here would be a guess. Conversions will be counted; revenue will not.
    // See the note in SEO_AUDIT.md for the accurate way to get revenue.
    function trackPurchase() {
        var path = window.location.pathname;
        if (path.indexOf('/success') === -1 && path.indexOf('thank-you') === -1) return;

        var params = new URLSearchParams(window.location.search);
        var sessionId = params.get('session_id') || params.get('checkout_session_id');
        var key = 'purchase_tracked:' + (sessionId || path);

        try {
            if (window.sessionStorage.getItem(key)) return;   // already counted
            window.sessionStorage.setItem(key, '1');
        } catch (e) {
            // Private mode or blocked storage: better to count a refresh twice
            // than to lose the conversion entirely.
        }

        var payload = { event_category: 'conversion', currency: 'USD' };
        if (sessionId) payload.transaction_id = sessionId;
        gtag('event', 'purchase', payload);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trackPurchase);
    } else {
        trackPurchase();
    }

})();
