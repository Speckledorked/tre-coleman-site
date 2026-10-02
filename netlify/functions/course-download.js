/**
 * Serves the paid course files, to buyers only.
 *
 * Before this existed, the 26 files under course/downloads/ were plain static
 * assets. The course pages checked `has_course_access` in the browser and
 * redirected if it was false, but that check only ever hid the links: a direct
 * request for the file answered 200 to anyone. The X-Robots-Tag header kept
 * them out of search results, which is not the same as keeping them private.
 *
 * Netlify serves everything in the publish directory, and the publish
 * directory here is the repository root, so there is nowhere in the repo a
 * file can sit and not be served. What makes the gate real is the forced
 * rewrite in netlify.toml: a redirect with force = true takes precedence over
 * a static file at the same path, so every request for /course/downloads/*
 * arrives here instead of hitting the asset. The files stay where they are and
 * stop being reachable without a token.
 *
 * Auth reuses the model the rest of the course already uses — the Supabase
 * access token from the login response, sent as a Bearer header. An <a href>
 * cannot send a header, so course/downloads.js intercepts the click and
 * fetches with one. That is why these links now require JavaScript; every
 * page carrying them already did, since the page itself does not render until
 * verifySession() resolves.
 *
 * Deliberately NOT done: a token in the query string. It would make the links
 * work without JavaScript, and it would also put a live credential into
 * browser history, Netlify's access logs and any Referer header the file's
 * host sends onward.
 */

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

const MIME = {
  '.pdf': 'application/pdf',
  '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
};

/**
 * Netlify does not promise a working directory, and included_files land in
 * different places depending on the bundler. Rather than guess once and fail
 * at runtime, try the candidates at cold start and keep the one that exists.
 */
function findRoot() {
  const candidates = [
    path.join(process.cwd(), 'course', 'downloads'),
    path.join(__dirname, 'course', 'downloads'),
    path.join(__dirname, '..', '..', 'course', 'downloads'),
  ];
  for (const dir of candidates) {
    try {
      if (fs.statSync(dir).isDirectory()) return dir;
    } catch (_) { /* try the next one */ }
  }
  return null;
}

/**
 * The set of files that may be served, built by walking the directory once.
 *
 * An allowlist rather than path sanitising: a request is answered only if it
 * matches a path that actually exists under the root, so "../" and its encoded
 * forms cannot name anything, because nothing outside the walk is ever in the
 * set. There is no pattern to get wrong.
 */
function buildIndex(root) {
  const index = new Map();
  if (!root) return index;
  const walk = (dir, prefix) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isDirectory()) walk(path.join(dir, entry.name), rel);
      else if (entry.isFile()) index.set(rel, path.join(dir, entry.name));
    }
  };
  walk(root, '');
  return index;
}

const ROOT = findRoot();
const FILES = buildIndex(ROOT);

const json = (statusCode, body) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  body: JSON.stringify(body),
});

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
      body: '',
    };
  }

  if (event.httpMethod !== 'GET') {
    return json(405, { error: 'Method not allowed' });
  }

  // The rewrite passes the path as ?file=; fall back to the request path so a
  // direct call to the function still works.
  let requested = (event.queryStringParameters || {}).file || '';
  if (!requested && event.path) {
    const marker = '/course/downloads/';
    const at = event.path.indexOf(marker);
    if (at !== -1) requested = event.path.slice(at + marker.length);
  }
  try {
    requested = decodeURIComponent(requested);
  } catch (_) {
    return json(400, { error: 'Malformed file name' });
  }
  requested = requested.replace(/^\/+/, '');

  if (!requested) return json(400, { error: 'No file requested' });

  // Resolve against the allowlist BEFORE authenticating, but answer 404 only
  // after, so an unauthenticated caller cannot use the response code to learn
  // which files exist.
  const resolved = FILES.get(requested);

  const authHeader = event.headers.authorization || event.headers.Authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return json(401, { error: 'Sign in to download course files' });
  }
  const token = authHeader.slice('Bearer '.length);

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY ||
      !process.env.SUPABASE_SERVICE_KEY) {
    console.error('course-download: Supabase environment variables are missing');
    return json(500, { error: 'Downloads are unavailable right now' });
  }

  let user;
  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);
    const { data, error } = await supabase.auth.getUser(token);
    if (error || !data || !data.user) {
      return json(401, { error: 'Your session has expired. Please sign in again.' });
    }
    user = data.user;
  } catch (err) {
    console.error('course-download: token verification failed', err);
    return json(500, { error: 'Downloads are unavailable right now' });
  }

  // has_course_access is read with the service key, exactly as auth-verify
  // does, so the answer does not depend on row-level security being right.
  let hasAccess = false;
  try {
    const service = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
    const { data: profile, error } = await service
      .from('users')
      .select('has_course_access')
      .eq('id', user.id)
      .single();
    if (error) {
      console.error('course-download: profile lookup failed', error);
      return json(500, { error: 'Downloads are unavailable right now' });
    }
    hasAccess = Boolean(profile && profile.has_course_access);
  } catch (err) {
    console.error('course-download: profile lookup threw', err);
    return json(500, { error: 'Downloads are unavailable right now' });
  }

  if (!hasAccess) {
    return json(403, { error: 'This file is part of the Catering Profit System' });
  }

  if (!ROOT) {
    console.error('course-download: course/downloads was not found in the bundle');
    return json(500, { error: 'Downloads are unavailable right now' });
  }
  if (!resolved) return json(404, { error: 'No such file' });

  let body;
  try {
    body = fs.readFileSync(resolved);
  } catch (err) {
    console.error('course-download: read failed for', requested, err);
    return json(500, { error: 'Downloads are unavailable right now' });
  }

  const name = path.basename(resolved);
  return {
    statusCode: 200,
    headers: {
      'Content-Type': MIME[path.extname(name).toLowerCase()] || 'application/octet-stream',
      'Content-Disposition': `attachment; filename="${name.replace(/"/g, '')}"`,
      'Content-Length': String(body.length),
      // A paid file must never be stored by a shared cache.
      'Cache-Control': 'private, no-store',
      'X-Robots-Tag': 'noindex, nofollow',
    },
    body: body.toString('base64'),
    isBase64Encoded: true,
  };
};
