// Generates references/v703-validation-rules.md from the bundled validator.
// Run after refreshing scripts/WAFlowJSONValidator_bundle.js.

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const src = fs.readFileSync(path.join(root, 'scripts/WAFlowJSONValidator_bundle.js'), 'utf8');

// ── 1. Parse all __d() modules into { name, deps, body } ───────────────────
const modules = {};
const moduleRe = /__d\("([A-Za-z0-9_.\$]+)",\[([^\]]*)\],\(function\([^)]*\)\{(.*?)\}\),\d+\);/gs;
let m;
while ((m = moduleRe.exec(src))) {
  const [, name, depsRaw, body] = m;
  const deps = (depsRaw.match(/"([^"]+)"/g) || []).map(s => s.slice(1, -1));
  modules[name] = { name, deps, body };
}

// ── 2. Walk chain lineage rooted at V703 ───────────────────────────────────
function walkChains(name, out = []) {
  if (out.includes(name)) return out;
  out.push(name);
  for (const d of (modules[name]?.deps || [])) {
    if (d.startsWith('WAFlowJSONValidatorChain')) walkChains(d, out);
  }
  return out;
}
const chains = walkChains('WAFlowJSONValidatorChainV703');

// ── 3. Collect validators referenced by any chain in lineage ────────────────
const validators = new Set();
for (const c of chains) {
  for (const d of (modules[c]?.deps || [])) {
    if (/Validator|Validation/.test(d) && !d.startsWith('WAFlowJSONValidatorChain') &&
        d !== 'WAFlowJSONValidationError' && d !== 'WAFlowJSONValidationResultUtil') {
      validators.add(d);
    }
  }
}

// ── 4. Pull error codes & messages from WAFlowJSONValidationError ──────────
const errBody = modules['WAFlowJSONValidationError'].body;
const codeBlock = errBody.match(/s=Object\.freeze\(\{([^}]+)\}\)/);
const errorCodes = [];
if (codeBlock) {
  const re = /([A-Z_]+):"([^"]+)"/g;
  let mm;
  while ((mm = re.exec(codeBlock[1]))) errorCodes.push({ key: mm[1], value: mm[2] });
}

// ── 5. For each validator, look up which error codes its body references ───
const errCodeKeys = errorCodes.map(e => e.key);
function codesFor(validatorName) {
  const body = modules[validatorName]?.body || '';
  const used = new Set();
  for (const k of errCodeKeys) {
    if (body.includes('WA_FLOW_JSON_VALIDATION_ERROR_CODE.' + k) ||
        body.includes(k + ':') && body.includes('WAFlowJSONValidationError')) {
      // narrow: require explicit ERROR_CODE.X
      if (body.includes('ERROR_CODE.' + k)) used.add(k);
    }
  }
  return [...used];
}

// ── 6. Humanize validator name → short description ─────────────────────────
function humanize(name) {
  let n = name.replace(/^WAFlowJSON/, '').replace(/^WAFlows?/, '').replace(/Validator(V\d+)?$/, '').replace(/V\d+$/, '');
  // split CamelCase
  return n.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/([A-Z])([A-Z][a-z])/g, '$1 $2');
}

// ── 7. Render markdown ─────────────────────────────────────────────────────
const lines = [];
lines.push('# Flow JSON v7.3 — applied validation rules');
lines.push('');
lines.push('Reverse-engineered from Meta\'s `WAFlowJSONValidatorChainV703`. Lists every validator the official Meta Flow Builder runs on a Flow JSON declaring `"version": "7.3"`, plus the full error-code dictionary.');
lines.push('');
lines.push('> Source: `scripts/WAFlowJSONValidator_bundle.js`. Regenerate with `node scripts/_extract_v703_rules.js`.');
lines.push('');
lines.push('---');
lines.push('');
lines.push('## Chain lineage');
lines.push('');
lines.push('V703 inherits all validators from earlier chains. Newer chains add or replace rules; nothing is removed implicitly.');
lines.push('');
for (const c of chains) lines.push(`- \`${c}\``);
lines.push('');
lines.push('---');
lines.push('');
lines.push('## Validators applied to v7.3 (' + validators.size + ')');
lines.push('');
lines.push('| Validator | What it checks | Error codes |');
lines.push('|---|---|---|');
for (const v of [...validators].sort()) {
  const desc = humanize(v);
  const codes = codesFor(v);
  lines.push(`| \`${v}\` | ${desc} | ${codes.length ? codes.map(c => '`' + c + '`').join(', ') : '—'} |`);
}
lines.push('');
lines.push('---');
lines.push('');
lines.push('## Full error-code dictionary');
lines.push('');
lines.push('All codes the validator can emit. Use this to interpret `errors[].code` from `run_validator.js` output.');
lines.push('');
lines.push('| Code | Internal value |');
lines.push('|---|---|');
for (const { key, value } of errorCodes) {
  lines.push(`| \`${key}\` | \`${value}\` |`);
}
lines.push('');
lines.push('---');
lines.push('');
lines.push('## How to use this reference');
lines.push('');
lines.push('1. Run `node scripts/run_validator.js <flow.json>` — output includes an `errors` array.');
lines.push('2. Each error has a `code` — look it up in the table above to confirm what failed.');
lines.push('3. To dig deeper, search `scripts/WAFlowJSONValidator_bundle.js` for the validator name from the first table; its `validate()` function holds the exact rule.');
lines.push('');

const out = path.join(root, 'references/v703-validation-rules.md');
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, lines.join('\n'));
console.log('wrote:', out);
console.log('chains:', chains.length, 'validators:', validators.size, 'error codes:', errorCodes.length);
