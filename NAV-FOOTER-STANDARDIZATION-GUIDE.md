# Navigation & Footer Standardization Guide

This document provides exact instructions for standardizing the navigation and footer across all HTML files on TreColeman.com.

## Problem
Currently, only **index.html** has the updated navigation structure. All other pages still have the old navigation:

**OLD NAVIGATION (needs replacing):**
- Services | Audits ▾ | Advisory | Resources ▾ | About | Contact | Book Your Snapshot

**NEW NAVIGATION (correct):**
- **Snapshot** | Services | Advisory | **Insights** ▾ | About | Contact

## Solution: Copy/Replace These Sections

### 1. NAVIGATION HTML (Lines ~203-225 in most files)

Find the `<nav id="mainNav">` section and replace the `<ul>` contents with:

```html
<ul>
    <li><a href="profit-leak-snapshot.html" class="nav-cta">Snapshot</a></li>
    <li><a href="services.html">Services</a></li>
    <li><a href="advisory.html">Advisory</a></li>
    <li class="nav-dropdown">
        <a href="#" onclick="return false;">Insights</a>
        <div class="dropdown-menu">
            <a href="playbook.html">Free Playbook</a>
            <a href="catering-profit.html">Catering Profit System</a>
        </div>
    </li>
    <li><a href="about.html">About</a></li>
    <li><a href="contact.html">Contact</a></li>
</ul>
```

**Key Changes:**
- `Snapshot` is now FIRST (was last as "Book Your Snapshot")
- `Audits` dropdown removed (pages still exist, just not in nav)
- `Resources` renamed to `Insights`
- Simpler structure: 6 top-level items, 1 dropdown

### 2. FOOTER HTML (Lines ~350-400 in most files)

Find the `<footer>` section and replace with the standardized footer from index.html:

```html
<footer>
    <div class="footer-content">
        <div class="footer-section">
            <h3>Tre Coleman Consulting LLC</h3>
            <p>Richmond/Charlottesville, VA</p>
            <p>Serving Nationwide</p>
            <p style="margin-top: 1rem;">© 2026. All Rights Reserved</p>
        </div>

        <div class="footer-section">
            <h4>Quick Links</h4>
            <ul>
                <li><a href="services.html">Services</a></li>
                <li><a href="advisory.html">Advisory</a></li>
                <li><a href="profit-leak-snapshot.html">Profit Leak Snapshot</a></li>
                <li><a href="catering-profit.html">Catering Course</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>

        <div class="footer-section">
            <h4>Connect</h4>
            <ul>
                <li><a href="mailto:hello@trecoleman.com">hello@trecoleman.com</a></li>
                <li><a href="tel:540.807.9045">540.807.9045</a></li>
                <li><a href="https://www.linkedin.com/in/tre-coleman/" target="_blank">LinkedIn</a></li>
                <li><a href="https://www.facebook.com/TreColemanConsulting" target="_blank">Facebook</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>Real restaurant experience. Real results.</p>
    </div>
</footer>
```

## Files That Need Updates

### High Priority (Customer-Facing Pages)
1. ✅ **index.html** - DONE (already has correct nav/footer)
2. ❌ **services.html** - Needs nav & footer update
3. ❌ **advisory.html** - Needs nav & footer update
4. ❌ **about.html** - Needs nav & footer update
5. ❌ **contact.html** - Needs nav & footer update
6. ❌ **blog.html** - Needs nav & footer update
7. ❌ **profit-leak-snapshot.html** - Needs nav & footer update

### Medium Priority (Tool/Resource Pages)
8. ❌ **audit.html** - Needs nav & footer update
9. ❌ **playbook.html** - Needs nav & footer update
10. ❌ **catering-profit.html** - Needs nav & footer update
11. ❌ **chat.html** - Needs nav & footer update
12. ❌ **ai-integration.html** - Needs nav & footer update

### Lower Priority (Specialty Pages)
13. ❌ **food-truck-audit.html** - Needs nav & footer update
14. ❌ **404.html** - Needs nav & footer update
15. ❌ **exit-intent-popup.js** - Check if nav refs need updating

## How to Do This Efficiently

### Option 1: VS Code Multi-File Find & Replace (FASTEST - 5 minutes)

1. Clone the repo locally
2. Open in VS Code
3. Use Find & Replace (Ctrl+Shift+F):
   - Search for: `<nav id="mainNav">` (to locate each nav)
   - Manually replace each nav `<ul>` section with the new HTML above
4. Repeat for footer sections
5. Commit and push

### Option 2: Script Approach (5-10 minutes)

Create a simple find/replace script:

```bash
# Save the correct nav HTML to a file
# Run a script to replace in all HTML files
for file in *.html; do
  # Replace navigation section
  sed -i '/<nav id="mainNav">/,/<\/nav>/c\[NEW NAV HTML]' "$file"
  # Replace footer section
  sed -i '/<footer>/,/<\/footer>/c\[NEW FOOTER HTML]' "$file"
done
```

### Option 3: Manual Through GitHub Web Editor (SLOW - 1+ hour)

Edit each file one-by-one through GitHub's web interface. Not recommended.

## Quick Validation

After updating, verify on each page:
- ✅ Navigation shows: **Snapshot | Services | Advisory | Insights | About | Contact**
- ✅ "Insights" dropdown works and shows "Free Playbook" and "Catering Profit System"
- ✅ "Audits" dropdown is gone from top nav
- ✅ Footer links match across all pages
- ✅ Footer shows "Richmond/Charlottesville, VA | Serving Nationwide"

## Why This Matters

Inconsistent navigation creates:
- ❌ Confusion for visitors (different menus on different pages)
- ❌ Broken user mental models
- ❌ Unprofessional appearance
- ❌ Navigation drift (changes only applied to some pages)

Standardized navigation provides:
- ✅ Clear, predictable site structure
- ✅ Professional, polished experience
- ✅ Easier future updates (change once, apply everywhere)
- ✅ Better SEO (consistent internal linking)

---

**Implementation Status:** 📝 Documentation complete, awaiting execution

**Estimated Time:** 5-10 minutes with proper tooling

**Priority:** HIGH - Inconsistent navigation is confusing users
