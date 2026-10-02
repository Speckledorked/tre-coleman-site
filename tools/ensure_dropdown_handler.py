#!/usr/bin/env python3
"""
Give every page with a mobile nav the dropdown tap handler.

On a touch screen the three dropdown parents have to toggle their submenu
rather than follow their own href. Thirty-four pages carry an inline handler
that does this. privacy.html did not, so tapping "Services" in its mobile menu
navigated straight to services.html and the seven service links under it could
not be reached from that page at all.

Verified before the fix, at 390x844: tapping Services on privacy.html moved the
browser from /privacy.html to /services.html.

The handler is injected per page rather than moved into the shared nav-aria.js,
because the other thirty-four already bind their own and a second listener
would toggle the class twice on every tap — leaving the submenu exactly as it
was. Shared code cannot tell from the DOM whether an inline handler is already
attached, so the safe move is to make the odd page out match the rest.

Run from the repository root:

    python3 tools/ensure_dropdown_handler.py
"""

import glob
import os
import re

MARKER = "tools/ensure_dropdown_handler.py"

HANDLER = """<script>
  /* Added by %s — see that file for why this is inline. */
  document.querySelectorAll('.nav-dropdown > a').forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      if (window.innerWidth <= 1024) {
        e.preventDefault();
        var open = toggle.parentElement.classList.toggle('active');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
    });
  });
</script>
""" % MARKER


def has_handler(page):
    """An inline listener is already bound to the dropdown parents.

    Both existing shapes select the same way — querySelectorAll('.nav-dropdown
    > a') — whether the result is stored in a variable first or iterated
    directly, so matching the selector is enough.
    """
    return bool(re.search(
        r"""querySelectorAll\(\s*['"]\.nav-dropdown\s*>\s*a['"]\s*\)""", page))


def main():
    changed = 0
    for path in sorted(glob.glob("*.html") + glob.glob("blog/*.html")
                       + glob.glob("course/*.html")):
        with open(path, encoding="utf-8") as fh:
            page = fh.read()

        if "mobileMenuToggle" not in page or "nav-dropdown" not in page:
            continue
        if MARKER in page or has_handler(page):
            continue
        if "</body>" not in page:
            print(f"  {path:<44} SKIPPED — no </body>")
            continue

        page = page.replace("</body>", HANDLER + "</body>", 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"  {os.path.basename(path):<44} dropdown handler added")
        changed += 1

    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
