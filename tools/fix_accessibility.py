#!/usr/bin/env python3
"""
Accessibility and semantic-HTML pass.

Applies, across every page that can safely take them:

  * <main> landmark wrapping the content between </header> and <footer>,
    so screen readers can jump to the content and Google can identify the
    page's main content region
  * a skip-to-content link as the first focusable element
  * footer column headings promoted from <h4> to <h2>. They were <h4> with
    no <h2>/<h3> above them, which on thin pages meant the heading outline
    jumped straight from <h1> to <h4>
  * role="button" / aria-haspopup / aria-expanded on the nav dropdown
    toggles. They are <a href="#"> elements that do not navigate; the ARIA
    attributes tell assistive tech what they actually are.
    (Left as anchors rather than real <button>s because the nav CSS is
    keyed on `#mainNav a` — converting the element would need a CSS rewrite
    for no additional accessibility gain.)
  * aria-expanded kept in sync by the existing mobile dropdown handler

Run from the repository root:

    python3 tools/fix_accessibility.py
"""

import glob
import re

SKIP_LINK = '<a class="skip-link" href="#main-content">Skip to content</a>\n'

DROPDOWN_TOGGLE = re.compile(
    r'<a href="#" onclick="return false;">([^<]+)</a>', re.I
)

# The mobile dropdown handler, present inline on most pages.
OLD_HANDLER = re.compile(
    r'(dropdownToggles\.forEach\(toggle => \{\s*'
    r'toggle\.addEventListener\(\'click\', \(e\) => \{\s*'
    r'if \(window\.innerWidth <= 1024\) \{\s*'
    r'e\.preventDefault\(\);\s*'
    r'toggle\.parentElement\.classList\.toggle\(\'active\'\);\s*'
    r'\}\s*\}\);\s*\}\);)',
    re.S,
)

NEW_HANDLER = """dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
          if (window.innerWidth <= 1024) {
            e.preventDefault();
            const open = toggle.parentElement.classList.toggle('active');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
          }
        });
      });"""


def add_main(html):
    if "<main" in html:
        return html, False
    low = html.lower()
    if low.count("</header>") != 1 or low.count("<footer") != 1:
        return html, False
    end_header = low.find("</header>") + len("</header>")
    start_footer = low.find("<footer")
    if end_header >= start_footer:
        return html, False
    return (
        html[:end_header]
        + '\n<main id="main-content">'
        + html[end_header:start_footer]
        + "</main>\n"
        + html[start_footer:]
    ), True


def add_skip_link(html):
    if "skip-link" in html:
        return html, False
    match = re.search(r"<body[^>]*>", html, re.I)
    if not match:
        return html, False
    return html[: match.end()] + "\n" + SKIP_LINK + html[match.end():], True


def promote_footer_headings(html):
    """<h4> inside .footer-section are section headings, not level-4."""
    def repl(match):
        return match.group(0).replace("<h4>", "<h2>").replace("</h4>", "</h2>")

    new = re.sub(
        r'<div class="footer-section">.*?</div>',
        repl,
        html,
        flags=re.S,
    )
    return new, new != html


def annotate_dropdowns(html):
    new = DROPDOWN_TOGGLE.sub(
        lambda m: (
            f'<a href="#" onclick="return false;" role="button" '
            f'aria-haspopup="true" aria-expanded="false">{m.group(1)}</a>'
        ),
        html,
    )
    new2 = OLD_HANDLER.sub(lambda _: NEW_HANDLER, new)
    return new2, new2 != html


def main():
    counts = {}
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        original = html
        applied = []

        for name, fn in (
            ("main", add_main),
            ("skip", add_skip_link),
            ("footer-h2", promote_footer_headings),
            ("aria", annotate_dropdowns),
        ):
            html, did = fn(html)
            if did:
                applied.append(name)
                counts[name] = counts.get(name, 0) + 1

        if html != original:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print(f"  {path:<52} {' '.join(applied)}")

    print()
    for key, num in sorted(counts.items()):
        print(f"{num:3d}  {key}")


if __name__ == "__main__":
    main()
