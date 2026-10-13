/**
 * Runtime audit of the mobile navigation, in both themes and both states.
 *
 * WHY THIS EXISTS
 *
 * The navigation has now broken four separate times, and every static or
 * automated check the repository had passed cleanly through all four:
 *
 *   1. The panel rendered near-white on near-white in dark mode, because
 *      style.css:931 hardcoded a light gradient. Caught by a photograph of a
 *      phone, not by a check.
 *   2. Every contrast sweep filtered elements on `offsetParent`, which is null
 *      for anything hidden until interaction. The navigation panel is hidden
 *      until tapped, so "0 failures across 13 pages" was true of what it
 *      measured and blind to the menu entirely.
 *   3. A sweep for hardcoded whites was case-sensitive and never matched
 *      `#FAFAF8` or `#F5F5F3`.
 *   4. The toggle's three bars and the button behind them both resolved to
 *      var(--ink) -- 1.00:1, the icon invisible in BOTH themes, with only a
 *      box-shadow tracing a ghost of it. A foreground-vs-background text
 *      audit could never have caught this one: the bars are not text, they
 *      are spans with a background-color.
 *
 * So this measures the rendered result in a real browser, with the menu both
 * shut AND open, and treats the bars as the UI component they are. It also
 * checks the things that made the fourth bug invisible for as long as it was:
 * whether the close affordance is on top and actually hittable, and whether
 * anything in the panel sits underneath it.
 *
 * NO NEW DEPENDENCY. CI installs playwright with --no-save, the same way the
 * Lighthouse and link jobs use npx: package.json still carries only the three
 * runtime dependencies the Netlify Functions need.
 *
 * Run locally (from the repository root):
 *
 *     npm install --no-save playwright@1.63.x
 *     npx playwright install chromium
 *     node tools/check_nav_contrast.js
 */

'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

/* Pages with structurally different heads and stylesheet sets, so a
   regression that reaches one family and not another still gets caught:
   index.html is hand-built and carries inline CSS; contact.html has none at
   all and is styled purely from style.css; blog posts have their heads
   rewritten by build_articles.py and still load the older font stack.
   Course pages are deliberately absent -- they have no mobile nav at all, so
   including one would only add a silent skip. */
const PAGES = [
  'index.html',
  'catering-profit.html',
  'contact.html',
  'blog/menu-engineering-guide.html',
];

const THEMES = ['light', 'dark'];

/* WCAG 2.1: 4.5:1 for body text, 3:1 for the graphical parts of a UI
   component (1.4.11). The bars are the icon, so they are the 3:1 case. */
const TEXT_MIN = 4.5;
const UI_MIN = 3.0;

/* WCAG 2.5.8 asks 24x24; Apple's and Google's guidance both ask 44. The
   toggle was deliberately sized to 44 at style.css:175 and a later rule
   inflated it to 77x49, so assert the floor, not an exact size. */
const TARGET_MIN = 44;

const MIME = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.webp': 'image/webp',
  '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2',
  '.xml': 'application/xml', '.txt': 'text/plain', '.ico': 'image/x-icon',
};

function serve(root) {
  const server = http.createServer((req, res) => {
    let rel = decodeURIComponent(req.url.split('?')[0]);
    if (rel.endsWith('/')) rel += 'index.html';
    // Resolve inside root, so a traversal in a href cannot read outside it.
    const file = path.join(root, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''));
    if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404).end('not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

/* --- contrast ------------------------------------------------------------ */

function channel(v) {
  const c = v / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function luminance([r, g, b]) {
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function contrast(a, b) {
  const [l1, l2] = [luminance(a), luminance(b)];
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

/** "rgb(26, 25, 23)" / "rgba(26, 25, 23, 0.9)" -> [26, 25, 23] */
function rgb(value) {
  const parts = (value.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
  return parts.length === 3 ? parts : null;
}

/* --- the measurements, taken in the page ---------------------------------- */

/* Runs in the browser. Returns raw colours and geometry; the comparing and
   judging happens in Node, so a failure prints real numbers. */
function probe() {
  const toggle = document.getElementById('mobileMenuToggle');
  const nav = document.getElementById('mainNav');
  if (!toggle || !nav) return { skip: 'no mobile navigation on this page' };

  // The background actually painted behind an element: walk up until an
  // ancestor has a non-transparent background. This is what an audit reading
  // only the element's own background-color gets wrong.
  const behind = (el) => {
    let node = el;
    while (node && node !== document.documentElement) {
      const bg = getComputedStyle(node).backgroundColor;
      if (bg && !/rgba\(0, 0, 0, 0\)|transparent/.test(bg)) return bg;
      node = node.parentElement;
    }
    return getComputedStyle(document.documentElement).backgroundColor || 'rgb(255, 255, 255)';
  };

  const open = nav.classList.contains('active');
  const box = toggle.getBoundingClientRect();

  // Only bars that are actually drawn: the middle one is opacity 0 in the X.
  const bars = [...toggle.querySelectorAll('span')]
    .filter((s) => getComputedStyle(s).opacity !== '0')
    .map((s) => {
      const r = s.getBoundingClientRect();
      return {
        colour: getComputedStyle(s).backgroundColor,
        // A bar sitting over the open panel is on the panel's ground, not the
        // header's, so measure against whatever is under the bar itself.
        against: open ? behind(nav) : behind(toggle),
        shadow: getComputedStyle(s).boxShadow,
        dx: +(r.x + r.width / 2 - (box.x + box.width / 2)).toFixed(1),
        dy: +(r.y + r.height / 2 - (box.y + box.height / 2)).toFixed(1),
      };
    });

  // Is the close affordance actually on top and hittable at its own centre?
  const cx = Math.round(box.x + box.width / 2);
  const cy = Math.round(box.y + box.height / 2);
  const atCentre = document.elementFromPoint(cx, cy);

  // Anything in the panel sitting under the button is both unreadable and
  // un-tappable, and it is what the panel's padding-top exists to prevent.
  const covered = [...nav.querySelectorAll('li')]
    .map((li) => {
      const r = li.getBoundingClientRect();
      const oy = Math.min(box.bottom, r.bottom) - Math.max(box.top, r.top);
      const ox = Math.min(box.right, r.right) - Math.max(box.left, r.left);
      return oy > 0 && ox > 0
        ? { text: li.textContent.trim().slice(0, 24).replace(/\s+/g, ' '), ox: Math.round(ox), oy: Math.round(oy) }
        : null;
    })
    .filter(Boolean);

  const links = [...nav.querySelectorAll('a')].map((a) => ({
    text: a.textContent.trim().slice(0, 24).replace(/\s+/g, ' '),
    colour: getComputedStyle(a).color,
    against: behind(a),
    size: parseFloat(getComputedStyle(a).fontSize),
    weight: getComputedStyle(a).fontWeight,
  }));

  return {
    open,
    width: Math.round(box.width),
    height: Math.round(box.height),
    ariaExpanded: toggle.getAttribute('aria-expanded'),
    hasActiveClass: toggle.classList.contains('active'),
    toggleOnTop: !!(atCentre && (atCentre === toggle || toggle.contains(atCentre))),
    atCentre: atCentre ? (atCentre.id || atCentre.className || atCentre.tagName) + '' : 'nothing',
    bars,
    covered,
    links,
  };
}

/* --- judging -------------------------------------------------------------- */

function judge(page, theme, state, d, fail) {
  const where = `${page} [${theme}, ${state}]`;

  if (d.width < TARGET_MIN || d.height < TARGET_MIN) {
    fail(`${where}: toggle is ${d.width}x${d.height}, below the ${TARGET_MIN}x${TARGET_MIN} target`);
  }

  if (!d.bars.length) {
    fail(`${where}: toggle has no visible bars at all`);
  }

  d.bars.forEach((bar, i) => {
    const fg = rgb(bar.colour);
    const bg = rgb(bar.against);
    if (!fg || !bg) {
      fail(`${where}: bar ${i + 1} has an unreadable colour (${bar.colour} on ${bar.against})`);
      return;
    }
    const ratio = contrast(fg, bg);
    if (ratio < UI_MIN) {
      fail(`${where}: bar ${i + 1} is ${ratio.toFixed(2)}:1 `
        + `(${bar.colour} on ${bar.against}), below ${UI_MIN}:1 for a UI component`);
    }
  });

  // The X must cross at the button's centre, or it reads as lopsided. 1.5px of
  // slack absorbs subpixel layout without admitting the 2.2px error that the
  // translate-inside-a-rotated-frame form produced.
  if (state === 'open') {
    d.bars.forEach((bar, i) => {
      if (Math.abs(bar.dx) > 1.5 || Math.abs(bar.dy) > 1.5) {
        fail(`${where}: X stroke ${i + 1} is offset (${bar.dx}, ${bar.dy})px from the button centre`);
      }
    });
    if (!d.hasActiveClass) {
      fail(`${where}: menu is open but the toggle has no .active class, `
        + `so the X transform never fires and the icon stays a hamburger`);
    }
    if (!d.toggleOnTop) {
      fail(`${where}: the open panel covers the close button `
        + `(elementFromPoint at its centre returned "${d.atCentre}"), so it cannot be tapped shut`);
    }
    d.covered.forEach((c) => {
      fail(`${where}: nav item "${c.text}" sits under the toggle (${c.ox}x${c.oy}px overlap)`);
    });
  }

  const expected = d.open ? 'true' : 'false';
  if (d.ariaExpanded !== expected) {
    fail(`${where}: aria-expanded is "${d.ariaExpanded}", expected "${expected}"`);
  }

  // Panel links are only rendered meaningfully once the menu is open; closed,
  // the panel is visibility:hidden and its colours are not what a user sees.
  if (state === 'open') {
    d.links.forEach((link) => {
      const fg = rgb(link.colour);
      const bg = rgb(link.against);
      if (!fg || !bg) return;
      const large = link.size >= 24 || (link.size >= 18.66 && Number(link.weight) >= 700);
      const min = large ? UI_MIN : TEXT_MIN;
      const ratio = contrast(fg, bg);
      if (ratio < min) {
        fail(`${where}: nav link "${link.text}" is ${ratio.toFixed(2)}:1 `
          + `(${link.colour} on ${link.against}), below ${min}:1`);
      }
    });
  }
}

/* --- run ------------------------------------------------------------------ */

async function main() {
  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (e) {
    console.error('playwright is not installed. From the repository root:\n'
      + '  npm install --no-save playwright@1.63.x\n'
      + '  npx playwright install chromium');
    process.exit(2);
  }

  const root = path.resolve(__dirname, '..');
  const { server, port } = await serve(root);
  const base = `http://127.0.0.1:${port}`;

  const failures = [];
  const fail = (message) => failures.push(message);
  let checked = 0;
  let skipped = 0;

  const browser = await chromium.launch();
  try {
    for (const theme of THEMES) {
      for (const page of PAGES) {
        const ctx = await browser.newContext({
          viewport: { width: 390, height: 844 },   // iPhone 12/13/14 logical size
          colorScheme: theme,
          reducedMotion: 'reduce',                 // land the slide instantly
        });
        const tab = await ctx.newPage();
        await tab.goto(`${base}/${page}`, { waitUntil: 'networkidle' });

        const shut = await tab.evaluate(probe);
        if (shut.skip) {
          skipped += 1;
          await ctx.close();
          continue;
        }
        judge(page, theme, 'closed', shut, fail);

        await tab.click('#mobileMenuToggle');
        await tab.waitForTimeout(400);
        const open = await tab.evaluate(probe);
        if (!open.open) {
          fail(`${page} [${theme}]: clicking the toggle did not open the menu`);
        } else {
          judge(page, theme, 'open', open, fail);
        }

        checked += 1;
        await ctx.close();
      }
    }
  } finally {
    await browser.close();
    server.close();
  }

  if (failures.length) {
    console.error(`\nFAILED — ${failures.length} problem(s) in the navigation:\n`);
    failures.forEach((f) => console.error(`  ${f}`));
    console.error('');
    process.exit(1);
  }

  console.log(`PASSED — navigation checked on ${checked} page/theme combination(s), `
    + `shut and open${skipped ? `, ${skipped} without a mobile nav` : ''}.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
