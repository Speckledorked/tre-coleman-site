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
        }
    });

    // Form submission tracking
    document.addEventListener('submit', function(e) {
        var form = e.target;
        gtag('event', 'form_submit', {
            event_category: 'engagement',
            event_label: form.id || form.getAttribute('name') || window.location.pathname,
            page_location: window.location.pathname
        });
    });
})();
