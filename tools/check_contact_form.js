#!/usr/bin/env node
/**
 * The contact function's field list must match the form's.
 *
 * An earlier draft invented a "timeline" field and omitted "budget" and
 * "start", both of which contact.html marks required. Nothing would have
 * failed: the form would submit, the email would send, and two answers the
 * buyer had given would simply be missing from it. That is the kind of fault
 * that is only ever found by a person noticing an email looks thin.
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'contact.html'), 'utf8');
const fn = fs.readFileSync(path.join(root, 'netlify/functions/contact-form.js'), 'utf8');

const problemsEarly = [];
const form = html.slice(html.indexOf('<form action'), html.indexOf('</form>'));
const fields = [...form.matchAll(/<(?:input|select|textarea)\b([^>]*)>/g)]
  .map((m) => m[1])
  .filter((a) => /name="/.test(a))
  .map((a) => ({
    name: a.match(/name="([^"]+)"/)[1],
    required: /\brequired\b/.test(a),
  }))
  // The honeypot is deliberately not a real field.
  .filter((f) => f.name !== 'website');

// The form's action is excluded from the link checker, because a serverless
// endpoint is not a file on disk and lychee can only report "File not found"
// for it. That exclusion must not mean nothing checks it, so the check moves
// here: a typo in the function name would otherwise post every enquiry into
// a 404.
const action = (form.match(/action="([^"]+)"/) || [])[1] || '';
if (!action) {
  problemsEarly.push('contact.html has no form action');
} else if (/^\/?\.netlify\/functions\//.test(action)) {
  const fnName = action.replace(/^\/?\.netlify\/functions\//, '').split('?')[0];
  const fnPath = path.join(root, 'netlify/functions', `${fnName}.js`);
  if (!fs.existsSync(fnPath)) {
    problemsEarly.push(`contact.html posts to "${action}" but netlify/functions/${fnName}.js does not exist`);
  }
} else if (/^https?:/i.test(action)) {
  problemsEarly.push(`contact.html posts to a third party (${action}); submissions are handled on this site`);
}

const listed = (which) => {
  const m = fn.match(new RegExp(`const ${which} = \\[([^\\]]*)\\]`, 's'));
  return m ? [...m[1].matchAll(/'([^']+)'/g)].map((x) => x[1]) : [];
};
const required = listed('REQUIRED');
const optional = listed('OPTIONAL');
const handled = new Set([...required, ...optional]);

const problems = [...problemsEarly];
for (const f of fields) {
  if (!handled.has(f.name)) problems.push(`contact.html has "${f.name}" but contact-form.js handles no such field`);
  if (f.required && !required.includes(f.name)) problems.push(`"${f.name}" is required on the form but not in the function's REQUIRED list`);
  if (!f.required && required.includes(f.name)) problems.push(`"${f.name}" is optional on the form but required by the function`);
}
const names = new Set(fields.map((f) => f.name));
for (const n of handled) {
  if (!names.has(n)) problems.push(`contact-form.js handles "${n}" but the form has no such field`);
}
// The honeypot must stay: it is the form's only spam defence.
if (!/name="website"/.test(form)) problems.push('the honeypot field is gone from contact.html');
if (!/position:absolute;left:-9999px/.test(form)) problems.push('the honeypot is no longer hidden');
if (!/fields\.website/.test(fn)) problems.push('contact-form.js no longer checks the honeypot');

if (problems.length) {
  console.error(`FAILED — contact form:\n${problems.map((p) => `  ${p}`).join('\n')}`);
  process.exit(1);
}
console.log(`PASSED — contact form: ${fields.length} field(s) agree between the form and the function.`);
