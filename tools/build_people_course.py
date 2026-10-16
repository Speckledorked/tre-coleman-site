#!/usr/bin/env python3
"""
Build the Catering People System's course pages under course/people/.

ONE-SHOT, like build_new_pages.py and NOT one of the eleven generators CI
runs. It is kept because it is how these seven pages were made and the
fastest way to re-make them if the structure has to change across all of
them at once -- but it OVERWRITES, so anything hand-edited into a page is
lost on a re-run. Read tools/README.md before running it again.

Run from the repository root:

    python3 tools/build_people_course.py

The pages differ from the Catering Profit System's in four ways, all of
them deliberate:

  - they live one directory deeper, so asset paths are ../../ and the
    shared scripts are ../auth.js and ../progress.js
  - they gate on CourseAuth.hasCourseAccess('catering-people') rather
    than the old single-course boolean, so owning the Profit course does
    not open them
  - there are no downloads, so there is no downloads sidebar and
    downloads.js is not loaded
  - the bonus page holds TWO lessons, which is why the registry lists
    bonus ids rather than deriving one
"""

import os
import re

OUT = "course/people"

COURSE_NAME = "The Catering People System"
COURSE_SHORT = "Catering People System"

MODULES = [
    {
        "n": 1,
        "title": "Lead Generation",
        "blurb": "Find buyers, position right, and book the call.",
        "learn": [
            "Where catering buyers actually look, and where they do not",
            "Positioning the same operation differently for corporate and private work",
            "An outreach system you can run every week without it going stale",
            "Turning an inquiry into a booked call instead of an unanswered email",
        ],
        "downloads": [
            "Ideal Buyer Map",
            "Corporate vs Private Positioning Sheet",
            "Weekly Outreach Tracker",
            "Venue Planner Partnership Pitch",
            "Inquiry Qualification Checklist",
        ],
        "lessons": [
            ("Where Catering Buyers Actually Are", "jVE3WPjTUqY"),
            ("Positioning for Corporate vs. Private Events", "Ufsth-BCHMo"),
            ("Outreach Systems That Work", "hoicpjXmkUA"),
            ("Converting Inquiries Into Booked Calls", "YVnHrzSM-p0"),
        ],
    },
    {
        "n": 2,
        "title": "Marketing",
        "blurb": "Build a brand that books gigs on repeat.",
        "learn": [
            "Messaging that says what you actually do, to the people who buy it",
            "Social media judged on bookings rather than on followers",
            "Flyers, materials and local presence that still earn their cost",
            "Asking for reviews on purpose, and answering the bad ones",
        ],
        "downloads": [
            "Brand Messaging Worksheet",
            "Social Content Calendar",
            "One-Page Menu Flyer Template",
            "Event Photo Shot List",
            "Review Response Playbook",
        ],
        "lessons": [
            ("Brand and Messaging for Caterers", "we4XJvu-IEk"),
            ("Social Media That Books Gigs", "6sSeD952ils"),
            ("Flyers, Materials, and Local Presence", "lM9gDvZ26cw"),
            ("Reviews and Reputation Management", "wghC00v7cZM"),
        ],
    },
    {
        "n": 3,
        "title": "Winning and Keeping Clients",
        "blurb": "Close the sale and keep them coming back.",
        "learn": [
            "Running the sales conversation without discounting your way into the job",
            "Proposals and pricing that hold up when the client pushes back",
            "A referral system that does not depend on remembering to ask",
            "Handling the difficult situations that decide whether they rebook",
        ],
        "downloads": [
            "Discovery Call Script",
            "Objection Response Sheet",
            "Client Expectations Agreement",
            "Event Timeline Confirmation",
            "Referral Program Tracker",
            "Difficult Client Playbook",
        ],
        "lessons": [
            ("The Sales Conversation", "lUoXU99b5VY"),
            ("Pricing and Proposals", "Xf-L4BFGGYM"),
            ("Referral Systems", "N_ac9LAdKPw"),
            ("Handling Difficult Client Situations", "T9TG7FZ61KA"),
        ],
    },
    {
        "n": 4,
        "title": "Hiring and Staffing",
        "blurb": "Hire right, onboard fast, and handle the hard exits.",
        "learn": [
            "Which role to fill next, and when the timing is actually right",
            "A hiring process that filters before it costs you a shift",
            "Onboarding that gets someone useful on their first event",
            "Letting someone go without damaging the rest of the team",
        ],
        "downloads": [
            "Job Post Templates",
            "Interview Question Bank and Scoring",
            "Role Scorecards",
            "Working Interview Checklist",
            "30-Day Onboarding Plan",
            "Separation Documentation Checklist",
        ],
        "lessons": [
            ("Who to Hire and When", "5oWmKuBYQBk"),
            ("The Hiring Process", "wnF_GwKLzZ8"),
            ("Onboarding and Training", "be0XEOu3tZc"),
            ("Letting Someone Go", "_0BSVBkhdPc"),
        ],
    },
    {
        "n": 5,
        "title": "Team and Culture",
        "blurb": "Build a team that stays and performs on event day.",
        "learn": [
            "What makes catering staff stay, when the pay is comparable everywhere",
            "Retention you can act on rather than hope for",
            "Holding people accountable without standing over them",
            "Leading the team on event day, when nothing goes to plan",
        ],
        "downloads": [
            "Team Standards Sheet",
            "Stay Interview Guide",
            "Recognition and Incentive Menu",
            "Weekly Check-In Template",
            "Event Day Pre-Shift Brief",
            "Post-Event Debrief Form",
        ],
        "lessons": [
            ("Building a Culture People Want to Stay In", "oRDWSc9aU4k"),
            ("Retention Strategies", "tFuqinXsB6s"),
            ("Accountability Without Micromanaging", "e3b-jn-Tv7Q"),
            ("Leading the Team on Event Day", "vp6zdQJxEu4"),
        ],
    },
]

BONUS = [
    ("Your 90-Day People Plan", "hIWKmty9Ohs"),
    ("Team Communication Toolkit", "ZmZSbmChNFg"),
]

BONUS_DOWNLOADS = [
    "90-Day People Plan",
    "Team Communication Toolkit",
    "Staff Roster Tracker",
]

# A YouTube id is 11 characters of [A-Za-z0-9_-]. Checked because a wrong id
# renders a dead player inside a paid course, and nothing else here would
# notice: the page is valid HTML either way and the embed fails silently.
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow" />
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
    <!-- Self-hosted variable fonts: same origin, two files, no third-party
         chain in the critical path. crossorigin is required on a font
         preload even same-origin. -->
    <link rel="preload" as="font" type="font/woff2" href="../../fonts/archivo-var-latin.woff2" crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="../../fonts/inter-var-latin.woff2" crossorigin>
    <link rel="stylesheet" href="../../ledger.css" />
  </head>
<body class="ledger">
<a class="skip-link" href="#main-content">Skip to content</a>
"""

# The gate names the course. Owning the Catering Profit System must not open
# these pages, which is the whole point of per-course access.
BOOT = """  <script src="../auth.js"></script>
  <!-- Intercepts download links and re-issues them with the Bearer token;
       an <a href> cannot send an Authorization header, and
       /course/downloads/* is a function, not a static file. -->
  <script src="../downloads.js"></script>
  <script src="../progress.js"></script>
  <script src="../upgrade.js"></script>
  <script>
    async function initPage() {{
      CourseAuth.init();
      const back = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
      if (!CourseAuth.isLoggedIn()) {{ window.location.href = back; return; }}
      const isValid = await CourseAuth.verifySession();
      if (!isValid) {{ window.location.href = back; return; }}
      if (!CourseAuth.hasCourseAccess('catering-people')) {{
        window.location.href = '/course/no-access.html?course=catering-people';
        return;
      }}
      document.getElementById('loading').style.display = 'none';
      document.getElementById('{page_id}').style.display = 'block';
      const nameEl = document.getElementById('user-name');
      if (nameEl) {{
        const u = CourseAuth.getUser();
        if (u && u.name) nameEl.textContent = u.name;
      }}
      CourseProgress.init();
      // Only the dashboard offers the other course; module pages do not.
      if (typeof CourseUpgrade !== 'undefined' && document.getElementById('dashboard')) {{
        CourseUpgrade.init();
      }}
    }}
    initPage();
  </script>
</body>
</html>
"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


DOWNLOAD_ROOT = "course/downloads/people"

MISSING = []


def slug(name):
    """'Corporate vs Private Positioning Sheet' -> 'Corporate_vs_Private_Positioning_Sheet'.

    Matches the Catering Profit System's convention
    (Event_Staffing_Calculator.xlsx), so both courses' files look the same in
    a downloads folder.
    """
    keep = [c for c in name if c.isalnum() or c in " -"]
    return "".join(keep).strip().replace(" ", "_")


# A download whose FILE is named differently from its label, where the
# difference is a real word rather than punctuation. Listed explicitly rather
# than matched loosely: dropping a word to make two names meet is how the
# wrong file ends up behind the right button.
FILE_OVERRIDES = {
    "Recognition and Incentive Menu": "Recognition_Incentive_Menu",
}


def norm(value):
    """Compare names ignoring punctuation only.

    The files use underscores where the labels use hyphens
    ("30-Day Onboarding Plan" -> 30_Day_Onboarding_Plan.docx). That is the
    same name written two ways, so matching through it is safe. Word
    differences are NOT bridged here -- those go in FILE_OVERRIDES where they
    can be seen.
    """
    return "".join(c for c in value.lower() if c.isalnum())


def find_download(folder, name):
    """The real file for a download, whatever extension it has.

    The extension is NOT assumed. These range from trackers that are
    obviously spreadsheets to scripts and playbooks that are obviously
    documents, and guessing .xlsx for a 'Discovery Call Script' would produce
    a link to a file that never arrives.

    Returns the filename, or None -- and a download with no file behind it is
    NOT written into the page. A dead link inside a paid course is worse than
    a missing row: course-download.js answers 404 for it, and the student is
    left clicking something that will never work. The missing ones are
    reported at the end instead.
    """
    base = FILE_OVERRIDES.get(name) or slug(name)
    folder_path = os.path.join(DOWNLOAD_ROOT, folder)
    if not os.path.isdir(folder_path):
        MISSING.append(f"{folder}/{base}.*")
        return []

    found = []
    for entry in sorted(os.listdir(folder_path)):
        stem, ext = os.path.splitext(entry)
        if ext and norm(stem) == norm(base):
            found.append(entry)

    if not found:
        MISSING.append(f"{folder}/{base}.*")
    return found


def downloads_card(folder, names):
    """The sidebar card, or nothing at all if no file exists yet."""
    rows = []
    for name in names:
        files = find_download(folder, name)
        for filename in files:
            # One template can ship in more than one format -- the 90-Day
            # People Plan is a PDF to read and a Word file to fill in. Label
            # the format when there is a choice, and say nothing when there
            # is not, so the common row stays clean.
            ext = os.path.splitext(filename)[1].lstrip(".").upper()
            label = f"{name} ({ext})" if len(files) > 1 else name
            href = f"../downloads/people/{folder}/{filename}"
            rows.append(
                f'            <li><span>&#128196; {esc(label)}</span>'
                f'<a href="{href}" download class="dl-btn">&#11015; Download</a></li>\n'
            )
    if not rows:
        return ""
    return ("""        <div class="sidebar-card">
          <h3>Downloads</h3>
          <ul class="download-list">
"""
            + "".join(rows)
            + """          </ul>
        </div>
""")


def sidebar_item(i, title):
    """One entry in the lessons list. The first is marked active, matching the
    Profit course's pages; progress.js adds is-done to the <li> as lessons are
    ticked off."""
    active = ' class="active"' if i == 0 else ""
    return (f'            <li><a href="#lesson-{i + 1}"{active}>'
            f"&#9654; {esc(title)}</a></li>\n")


def lesson_block(kind, index, title, vid, module_no=None):
    where = f"Module {module_no}, Lesson {index}" if module_no else f"Bonus {index}"
    return f"""        <div class="lesson-video" id="lesson-{index}">
          <h2>{kind} {index}: {esc(title)}</h2>
          <div class="video-embed">
            <iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/{vid}" title="{COURSE_SHORT} &mdash; {where}: {esc(title)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          </div>
        </div>
"""


def module_page(m):
    lessons = "".join(
        lesson_block("Lesson", i + 1, t, v, m["n"])
        for i, (t, v) in enumerate(m["lessons"])
    )
    sidebar = "".join(
        sidebar_item(i, t) for i, (t, _) in enumerate(m["lessons"])
    )
    learn = "".join(f"            <li>{esc(x)}</li>\n" for x in m["learn"])
    downloads = downloads_card(f"module-{m['n']}", m.get("downloads", []))

    nxt = (f'<a href="module-{m["n"] + 1}.html" class="nav-btn next">Next: '
           f'{esc(MODULES[m["n"]]["title"])} &rarr;</a>') if m["n"] < len(MODULES) else \
          '<a href="bonus.html" class="nav-btn next">Next: Bonus Material &rarr;</a>'
    prev = (f'<a href="module-{m["n"] - 1}.html" class="nav-btn prev">&larr; '
            f'{esc(MODULES[m["n"] - 2]["title"])}</a>') if m["n"] > 1 else "<span></span>"

    return (
        HEAD.format(title=f'Module {m["n"]} - {COURSE_NAME}',
                    description=esc(m["blurb"]))
        + f"""
  <div id="loading" class="loading">Loading module...</div>

  <div id="module-page" style="display: none;">
    <header class="module-header">
      <div class="header-content">
        <div class="header-nav">
          <a href="dashboard.html" class="back-btn">&larr; Back to Dashboard</a>
        </div>
        <button onclick="CourseAuth.logout()" class="logout-btn">Log Out</button>
      </div>
    </header>

    <section class="module-hero">
      <div class="module-hero-content">
        <span class="module-number">MODULE {m["n"]}</span>
        <h1>{esc(m["title"])}</h1>
        <p>{esc(m["blurb"])}</p>
      </div>
    </section>

    <div class="container">
      <main class="main-content" id="main-content">
        <div class="lesson-videos">
{lessons}        </div>
        <div class="lesson-content">
          <h2>What You&rsquo;ll Learn</h2>
          <ul>
{learn}          </ul>
        </div>
        <div class="nav-buttons">
          {prev}
          {nxt}
        </div>
      </main>
      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>Lessons</h3>
          <ul class="lessons-list">
{sidebar}          </ul>
        </div>
{downloads}      </aside>
    </div>
  </div>
"""
        + BOOT.format(page_id="module-page")
    )


def bonus_page():
    lessons = "".join(
        lesson_block("Bonus", i + 1, t, v) for i, (t, v) in enumerate(BONUS)
    )
    sidebar = "".join(sidebar_item(i, t) for i, (t, _) in enumerate(BONUS))
    downloads = downloads_card("bonus", BONUS_DOWNLOADS)
    return (
        HEAD.format(title=f"Bonus Material - {COURSE_NAME}",
                    description="Bonus material for the Catering People System.")
        + f"""
  <div id="loading" class="loading">Loading bonus material...</div>

  <div id="bonus-page" style="display: none;">
    <header class="module-header">
      <div class="header-content">
        <div class="header-nav">
          <a href="dashboard.html" class="back-btn">&larr; Back to Dashboard</a>
        </div>
        <button onclick="CourseAuth.logout()" class="logout-btn">Log Out</button>
      </div>
    </header>

    <section class="module-hero">
      <div class="module-hero-content">
        <span class="module-number">BONUS</span>
        <h1>Put It Into Practice</h1>
        <p>Two sessions for after the course: a plan for the first ninety days, and the communication tools to run it with.</p>
      </div>
    </section>

    <div class="container">
      <main class="main-content" id="main-content">
        <div class="lesson-videos">
{lessons}        </div>
        <div class="nav-buttons">
          <a href="module-5.html" class="nav-btn prev">&larr; Team and Culture</a>
          <a href="dashboard.html" class="nav-btn next">Back to Dashboard &rarr;</a>
        </div>
      </main>
      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>Sessions</h3>
          <ul class="lessons-list">
{sidebar}          </ul>
        </div>
{downloads}      </aside>
    </div>
  </div>
"""
        + BOOT.format(page_id="bonus-page")
    )


def dashboard_page():
    cards = ""
    for m in MODULES:
        items = "".join(
            f"              <li>{esc(t)}</li>\n" for t, _ in m["lessons"]
        )
        cards += f"""        <div class="module-card">
          <div class="module-header">
            <span class="module-number">Module {m["n"]}</span>
            <h3>{esc(m["title"])}</h3>
          </div>
          <div class="module-content">
            <p>{esc(m["blurb"])}</p>
            <ul class="module-deliverables">
{items}            </ul>
            <a href="module-{m["n"]}.html" class="module-btn">Go to Module {m["n"]} &rarr;</a>
          </div>
        </div>

"""
    return (
        HEAD.format(title=f"Course Dashboard - {COURSE_NAME}",
                    description="Your dashboard for the Catering People System.")
        + f"""
  <div id="loading" class="loading">Loading your course...</div>

  <div id="dashboard" style="display: none;">
    <header class="module-header">
      <div class="header-content">
        <!-- No link to the other course here. It used to be an
             unconditional "← The Catering Profit System", which pointed a
             People-only buyer at a dashboard that would greet them with the
             no-access overlay. upgrade.js now renders a link to the other
             course only when the account actually holds it. -->
        <div class="header-nav"></div>
        <button onclick="CourseAuth.logout()" class="logout-btn">Log Out</button>
      </div>
    </header>

    <main class="main-content" id="main-content">
      <section class="welcome-section">
        <h1>{COURSE_NAME}</h1>
        <h2>Welcome back, <span id="user-name">Student</span>!</h2>
        <p>Five modules on finding the work and building the team that delivers it. Two bonus sessions at the end.</p>
      </section>

      <!-- The module cards are h3, so this h2 is what keeps the outline from
           jumping h1 to h3. The Profit dashboard gets the same level from its
           "Welcome back" heading; check_site.py's html-a11y check caught the
           omission here. -->
      <h2 class="section-heading">Modules</h2>
      <section class="modules-grid">
{cards}      </section>

      <section class="welcome-section">
        <h2>Bonus Material</h2>
        <p>A ninety-day plan and a communication toolkit, for once you have been through the modules.</p>
        <a href="bonus.html" class="module-btn">Go to Bonus Material &rarr;</a>
      </section>
    </main>
  </div>
"""
        + BOOT.format(page_id="dashboard")
    )


def main():
    seen = set()
    for m in MODULES:
        for title, vid in m["lessons"]:
            assert ID_RE.match(vid), f"bad video id {vid!r} on {title!r}"
            assert vid not in seen, f"duplicate video id {vid!r} on {title!r}"
            seen.add(vid)
    for title, vid in BONUS:
        assert ID_RE.match(vid), f"bad video id {vid!r} on {title!r}"
        assert vid not in seen, f"duplicate video id {vid!r} on {title!r}"
        seen.add(vid)

    os.makedirs(OUT, exist_ok=True)
    written = []

    for m in MODULES:
        path = os.path.join(OUT, f"module-{m['n']}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(module_page(m))
        written.append(path)

    for name, html in (("bonus.html", bonus_page()),
                       ("dashboard.html", dashboard_page())):
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        written.append(path)

    for p in written:
        print(f"  {p}")
    print(f"  {len(written)} page(s), {len(seen)} unique video id(s)")

    if MISSING:
        print(f"\n  {len(MISSING)} download(s) have NO FILE and were left out "
              f"of the pages:")
        for m in MISSING:
            print(f"    {DOWNLOAD_ROOT}/{m}")
        print("\n  Drop the files in with those exact basenames (any "
              "extension) and re-run.")


if __name__ == "__main__":
    main()
