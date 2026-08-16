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
})();
