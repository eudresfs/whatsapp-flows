# validate

Run the official Meta Flow JSON validator and structural checks against a Flow JSON.

---

## Step 1 — Locate SKILL_DIR

The path to this file tells you where the skill lives. The scripts are at `<SKILL_DIR>/scripts/`.

---

## Step 2 — Check validator availability

```bash
node --version 2>/dev/null && \
  (ls <SKILL_DIR>/scripts/WAFlowJSONValidator_bundle.js 2>/dev/null || ls <SKILL_DIR>/scripts/WAFlowJSONValidator.js 2>/dev/null) && \
  echo "validator=available" || echo "validator=unavailable"
```

---

## Step 3a — Validator available: full validation

### Setup (once per session)

```bash
mkdir -p /tmp/wf-validator
cp <SKILL_DIR>/scripts/run_validator.js /tmp/wf-validator/
cp <SKILL_DIR>/scripts/package.json     /tmp/wf-validator/
# Copy whichever validator source exists (bundle preferred, legacy fallback)
cp <SKILL_DIR>/scripts/WAFlowJSONValidator_bundle.js /tmp/wf-validator/ 2>/dev/null
cp <SKILL_DIR>/scripts/WAFlowJSONValidator.js        /tmp/wf-validator/ 2>/dev/null
cd /tmp/wf-validator && npm install --silent
```

### Run

```bash
cat > /tmp/wf-validator/flow.json << 'EOF'
<FLOW_JSON_HERE>
EOF

node /tmp/wf-validator/run_validator.js /tmp/wf-validator/flow.json
```

### Interpreting results

**Success:**
```
✅ Flow JSON is valid (version 7.3)
```

**Semantic failure** — validator lists errors with location paths:
```
❌ Validation failed:
  - screens[0].layout.children[1].children[2]: "helper-text" is not allowed
  - screens[1].data.lista.items: must have required property 'properties'
```

For each error:
1. Locate the component by path (`screens[0].layout.children[1]`)
2. Consult `references/flow-json-reference.md` for the violated rule
3. Fix the JSON
4. Re-run validator

Repeat until `✅`.

**Syntax failure** (crash before validation):
```
SyntaxError: Unexpected token ...
```
Fix JSON syntax first (trailing comma, unclosed brace, etc.), then re-run.

If an error is not in the reference, inspect `run_validator.js` directly searching for the error message string to understand what it checks.

---

## Step 3b — Validator unavailable: structural checks

Print this message first:
```
⚠️ Validator source not found (looked for WAFlowJSONValidator_bundle.js and WAFlowJSONValidator.js). Running structural checks only.
To get the full validator, see scripts/README.md.
```

Then check these rules manually against the JSON:

### Structure
- [ ] `version` field present and is a string (e.g. `"7.3"`)
- [ ] `screens` is a non-empty array
- [ ] Every screen has `id` (letters + underscores only, no digits, no hyphens)
- [ ] Every screen has `title`
- [ ] Exactly one screen has `terminal: true`
- [ ] Terminal screen's Footer uses `"name": "complete"` (not `"navigate"`)
- [ ] Static flow: no `routing_model`, no `data_api_version`
- [ ] Endpoint flow: both `routing_model` and `data_api_version` present
- [ ] `routing_model.routes` covers all screen IDs referenced in `navigate` actions

### Navigation
- [ ] Every `navigate` action has `next` as an object `{"type": "screen", "name": "..."}`, not a string
- [ ] Destination screen declares in `data` every key from the navigate `payload`
- [ ] No orphaned screens (every non-first screen is reachable from a navigate action)

### Components
- [ ] Maximum 1 `Form` per screen
- [ ] Maximum 1 `Footer` per screen
- [ ] `Footer` is the last child of `Form` on screens that have a Form
- [ ] No `input-type: "date"` on `TextInput`
- [ ] `min-chars`, `max-chars`, `max-length` are numbers not strings
- [ ] `Switch` has a `"default"` case

### Data
- [ ] Every screen `data` field with arrays uses `items.properties` structure
- [ ] `__example__` present on all `data` fields (required by validator)

---

## Correction loop

After structural checks produce findings:

1. Fix each issue
2. Re-run validation (full or structural)
3. Repeat until clean

If stuck on a semantic error not covered by the reference, search `run_validator.js` for the exact error message string — the validation logic is readable once you find the right function.

---

## Delivering the result

After validation:
- `✅ valid` → suggest `audit` to check UX quality
- `❌ errors fixed` → show what changed + confirm `✅` before delivering new JSON
- `⚠️ structural only` → remind user to test in Flow Builder before publishing
