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
    """Guarantee exactly one #main-content, because the skip link targets it.

    The first version of this only handled the easy case — no <main> yet, and a
    single </header>…<footer> pair to wrap. It returned early on everything
    else, while add_skip_link ran unconditionally. The result was 20 pages
    carrying a skip link that pointed at a fragment the page did not contain:
    the first thing a keyboard user tabs to did nothing at all. lychee's
    --include-fragments is what caught it.

    So there are now three cases, tried in order:

      1. A <main> already exists and only needs the id (11 pages had a
         <main class="container"> from before this script existed).
      2. No <main>, but one </header>…<footer> pair to wrap. The original case.
      3. Neither — the auth pages, the course gate and the two app mounts have
         no header or footer at all. Wrap their primary content container.
         Wrapping rather than renaming keeps every existing CSS selector
         working; there are no `body > …` selectors in the stylesheet, so the
         extra level is inert.
    """
    if 'id="main-content"' in html:
        return html, False

    existing = re.search(r"<main\b([^>]*)>", html, re.I)
    if existing:
        return (
            html[: existing.start()]
            + "<main id=\"main-content\"" + existing.group(1) + ">"
            + html[existing.end():]
        ), True

    low = html.lower()
    if low.count("</header>") == 1 and low.count("<footer") == 1:
        end_header = low.find("</header>") + len("</header>")
        start_footer = low.find("<footer")
        if end_header < start_footer:
            return (
                html[:end_header]
                + '\n<main id="main-content">'
                + html[end_header:start_footer]
                + "</main>\n"
                + html[start_footer:]
            ), True

    span = find_content_container(html)
    if span:
        start, end = span
        return (
            html[:start]
            + '<main id="main-content">\n'
            + html[start:end]
            + '\n</main>'
            + html[end:]
        ), True

    return html, False


def top_level_elements(html):
    """(tag, attrs, start, end) for each direct child element of <body>."""
    body = re.search(r"<body[^>]*>", html, re.I)
    if not body:
        return []
    offset = body.end()
    rest = html[offset:]
    void = {
        "br", "img", "input", "meta", "link", "hr", "source", "area", "base",
        "col", "embed", "param", "track", "wbr",
    }
    out, depth, opened = [], 0, None
    for tag in re.finditer(r"<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>", rest):
        closing, name, attrs, self_closing = (
            tag.group(1), tag.group(2).lower(), tag.group(3), tag.group(4)
        )
        if name in void or self_closing:
            continue
        if not closing:
            if depth == 0:
                opened = (name, attrs, offset + tag.start())
            depth += 1
        else:
            depth -= 1
            if depth == 0 and opened and opened[0] == name:
                out.append((opened[0], opened[1], opened[2], offset + tag.end()))
                opened = None
            elif depth < 0:
                break
    return out


def find_content_container(html):
    """The (start, end) of the page's primary content wrapper.

    Prefer the last top-level <div> whose class contains "container" — that
    covers .container and .auth-container, and skips the modal and overlay
    divs that sit at the same level. Fall back to the last top-level <div>
    for the pages whose content wrapper is an app mount (#root, #vf) or an
    unclassed styled div.
    """
    divs = [e for e in top_level_elements(html) if e[0] == "div"]
    if not divs:
        return None
    named = [e for e in divs if re.search(r'class="[^"]*container', e[1])]
    tag, attrs, start, end = (named or divs)[-1]
    return start, end


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
