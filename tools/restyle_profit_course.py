#!/usr/bin/env python3
"""Apply the course shell to the hand-maintained Catering Profit pages.

The People course is generated from a manifest, so its pages picked up the
new shell by regenerating. The Profit pages are hand-written and carry copy
no manifest models -- the per-module framing paragraphs, the dashboard's
welcome video and launch notice -- so they are transformed in place rather
than regenerated. Rewriting them from a manifest would mean transcribing that
copy first, and anything missed would be silently dropped from a paid course.

IDEMPOTENT. A page that already carries `container course-grid` is skipped, so
running this twice does not insert a second index or a second rail.

Not one of the eleven generators CI runs. tools/check_courses.js asserts both
courses end up with the same shell, so the two cannot drift apart unnoticed.
"""

import io
import os
import re
import sys

MODULES = [
    (1, "Labor Cost Control"),
    (2, "Pricing That Actually Works"),
    (3, "Food Cost &amp; Menu Engineering"),
    (4, "Delivery &amp; Logistics Systems"),
    (5, "Cash Flow Management"),
]
BONUS_TITLE = "90-Day Implementation Plan"


def rail_modules(current):
    rows = []
    for n, title in MODULES:
        cur = ' class="is-current"' if current == n else ""
        rows.append(
            f'            <li{cur}><a href="module-{n}.html">'
            f'<span class="rail-modules__n">Module {n}</span>'
            f'<span class="rail-modules__t">{title}</span></a></li>\n'
        )
    cur = ' class="is-current"' if current == "bonus" else ""
    rows.append(
        f'            <li{cur}><a href="bonus.html">'
        f'<span class="rail-modules__n">Bonus</span>'
        f'<span class="rail-modules__t">{BONUS_TITLE}</span></a></li>\n'
    )
    return ('        <div class="sidebar-card">\n'
            '          <h3>Modules</h3>\n'
            '          <ol class="rail-modules">\n'
            + "".join(rows)
            + '          </ol>\n'
            '        </div>\n')


PROGRESS_PANEL = ('        <div class="sidebar-card" id="progress-panel">\n'
                  '          <h3>Your progress</h3>\n'
                  '        </div>\n')


def lesson_index(titles, kind="lesson"):
    """Rows built from the page's own lesson headings.

    No descriptions: unlike the People manifest, the Profit modules have no
    per-lesson copy to draw on -- their "What You'll Learn" bullets do not
    correspond one-to-one with the lessons -- and inventing a line per lesson
    is writing course copy, not restyling a page.
    """
    rows = []
    for i, title in enumerate(titles):
        rows.append(
            f'          <li>\n'
            f'            <span class="lesson-index__no">{i + 1:02d}</span>\n'
            f'            <div>\n'
            f'              <p class="lesson-index__title">'
            f'<a href="#{kind}-{i + 1}">{title}</a></p>\n'
            f'            </div>\n'
            f'            <a class="lesson-index__go" href="#{kind}-{i + 1}">'
            f'Start {kind} &rarr;</a>\n'
            f'          </li>\n'
        )
    return ('        <ol class="lesson-index">\n'
            + "".join(rows)
            + '        </ol>\n')


def strip_download_emoji(s):
    """The brief rules out emoji; these rendered as tofu boxes anyway."""
    s = s.replace('<li><span>&#128196; ', '<li><span>')
    s = s.replace('class="dl-btn">&#11015; Download</a>',
                  'class="dl-btn">Download</a>')
    return s


def drop_lessons_card(s):
    """Remove the sidebar lesson list; the numbered index replaces it.

    Keeping both would show the same four titles twice on one page, and
    progress.js marks whichever is present.
    """
    return re.sub(
        r'        <div class="sidebar-card">\n'
        r'          <h3>(?:Lessons|Sessions)</h3>\n'
        r'          <ul class="lessons-list">\n.*?'
        r'          </ul>\n'
        r'        </div>\n',
        '', s, flags=re.S)


def add_rail(s, current, with_progress=True):
    """Insert the rail panels ahead of whatever the sidebar already holds."""
    aside = '      <aside class="sidebar">\n'
    if aside not in s:
        return None
    panels = (PROGRESS_PANEL if with_progress else "") + rail_modules(current)
    return s.replace(aside, aside + panels, 1)


MAIN_OPEN = re.compile(r'(<main\b[^>]*\bid="main-content"[^>]*>\n)')


def transform(path, current):
    """A module page: the numbered index plus the rail."""
    s = io.open(path, encoding='utf-8').read()
    if 'container course-grid' in s:
        return False, 'already converted'

    titles = [t.strip() for t in re.findall(r'<h2>Lesson \d+:\s*(.*?)</h2>', s, re.S)]
    if not titles:
        return False, 'no lesson headings found'
    # The index links to the anchors the page already carries; if they are not
    # all there the links would be dead, so this refuses rather than guesses.
    missing = [i + 1 for i in range(len(titles))
               if f'id="lesson-{i + 1}"' not in s]
    if missing:
        return False, f'missing lesson anchors: {missing}'

    s = s.replace('<div class="container">', '<div class="container course-grid">', 1)
    m = MAIN_OPEN.search(s)
    if not m:
        return False, 'no main-content anchor'
    s = s[:m.end()] + lesson_index(titles) + s[m.end():]

    s = drop_lessons_card(s)
    s = strip_download_emoji(s)
    out = add_rail(s, current)
    if out is None:
        return False, 'no sidebar'
    io.open(path, 'w', encoding='utf-8').write(out)
    return True, 'converted'


def transform_bonus(path):
    """The Profit bonus is a written ninety-day roadmap, not video lessons.

    It gets the rail so a student can move between modules from it, and no
    lesson index, because there are no lessons on it to index.
    """
    s = io.open(path, encoding='utf-8').read()
    if 'container course-grid' in s:
        return False, 'already converted'
    s = s.replace('<div class="container">', '<div class="container course-grid">', 1)
    s = strip_download_emoji(s)
    out = add_rail(s, 'bonus', with_progress=False)
    if out is None:
        return False, 'no sidebar'
    io.open(path, 'w', encoding='utf-8').write(out)
    return True, 'converted'


def transform_dashboard(path):
    """The dashboard's module cards are its main column; it gains the rail.

    The existing sections are wrapped in a plain div rather than a <main>:
    the page already has one around the container, and a second would nest
    two <main> elements and fail check_site.py's structure count.
    """
    s = io.open(path, encoding='utf-8').read()
    if 'container course-grid' in s:
        return False, 'already converted'
    if '<div class="container">' not in s:
        return False, 'no container'

    s = s.replace('<div class="container">',
                  '<div class="container course-grid">\n      <div class="dash-main">', 1)
    close = '    </div>\n\n    <!-- Footer -->'
    if close not in s:
        return False, 'no closing anchor'
    s = s.replace(close,
                  '      </div>\n'
                  '      <aside class="sidebar">\n'
                  + PROGRESS_PANEL + rail_modules(None) +
                  '      </aside>\n'
                  '    </div>\n\n    <!-- Footer -->', 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    return True, 'converted'


def main():
    changed = 0
    failed = []
    for n, _title in MODULES:
        ok, why = transform(f'course/module-{n}.html', n)
        print(f'  course/module-{n}.html: {why}')
        changed += ok
        if not ok and why != 'already converted':
            failed.append(f'course/module-{n}.html: {why}')
    for fn, path in ((transform_bonus, 'course/bonus.html'),
                     (transform_dashboard, 'course/dashboard.html')):
        ok, why = fn(path)
        print(f'  {path}: {why}')
        changed += ok
        if not ok and why != 'already converted':
            failed.append(f'{path}: {why}')
    print(f'{changed} page(s) converted')
    if failed:
        print('FAILED:', *failed, sep='\n  ')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
