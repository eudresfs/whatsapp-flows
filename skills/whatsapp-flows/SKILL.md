---
name: whatsapp-flows
description: "Build, validate, audit and debug WhatsApp Flows JSON. Covers the full lifecycle: interviewing requirements, generating valid Flow JSON, running the official validator, auditing UX quality, and diagnosing broken flows. Use when the user is creating a WhatsApp Flow from scratch, fixing validator errors, auditing an existing flow for quality, troubleshooting screen navigation or data passing issues, or understanding component rules. Covers: static flows, endpoint-powered flows, all component types (TextInput, Dropdown, DatePicker, CalendarPicker, NavigationList, ChipsSelector, PhotoPicker, ImageCarousel, etc.), routing models, conditional rendering, media upload, and encryption."
version: 1.0.0
user-invocable: true
argument-hint: "[interview|build|validate|audit|debug]"
license: MIT
allowed-tools:
  - Bash(node scripts/run_validator.js *)
  - Bash(node .claude/skills/whatsapp-flows/scripts/load-context.mjs *)
---

# WhatsApp Flows

## Setup

Before any command, run the preflight. All gates must pass before generating or modifying JSON.

```bash
node .claude/skills/whatsapp-flows/scripts/load-context.mjs
```

| Gate | Check | If fail |
|---|---|---|
| **Language** | `languageSet` is true in config | Ask developer: "Which language? (PT-BR / EN)" then `--set-language` |
| **Register** | `registerSet` is true in config | Determine via `interview`; then `--set-register` |
| **Context** | Running `build`? Interview brief exists | Run `interview` first |
| **Mutation** | All gates above pass | Do not generate JSON until resolved |

Required preflight statement before any file mutation:

```
WF_PREFLIGHT: language=<lang> register=<static|endpoint> context=<pass|interview_needed> mutation=open
```

---

## Register

The register is the foundational split. Determine it in `interview`. Everything downstream branches on this.

### static

- No server required
- All data injected at send time via the API call payload
- Only `navigate` and `complete` actions
- No `routing_model`, no `data_api_version`
- Screen `data` fields declare schema + `__example__` only; no live data
- Prefer static whenever live server data is not required

### endpoint

- Server required; responds to `data_exchange` requests
- Conditional `routing_model` allowed (and required when using conditional routes)
- `data_api_version` required alongside `routing_model`
- Encryption mandatory (WACS public key)
- 10-second timeout per request — architecture must respect this
- First screen should be static (no data_exchange) to optimise opening latency

---

## Shared Flow Laws

These apply regardless of register.

### Structure
- `version`: `"7.3"` by default (string, not number)
- Every screen has `title` — required, no exceptions
- Screen IDs: letters and underscores only — `COLLECT_DATA` ✓ / `SCREEN_1` ✗ / `SCREEN-ONE` ✗
- Exactly one screen has `terminal: true`; its Footer uses `"name": "complete"`
- Maximum 1 Form per screen; maximum 1 Footer per screen; Footer is last child of Form

### Navigation
- `next` in navigate is always an object: `{"type": "screen", "name": "SCREEN_ID"}` — never a string
- Destination screen declares every payload field in its `data` with type + `__example__`
- `flow_token` expiry strategy must be defined — minimum 2–3 days recommended

### Components
- `helper-text` exists only on: TextInput, TextArea, DatePicker, CalendarPicker
- `input-type: "date"` does not exist — use DatePicker
- `min-chars`/`max-chars`/`max-length` are numbers, not strings
- `data-source` is the correct key (not `options`, `items`, `values`)
- Images via `data-source` ≤ 100KB (v6.0+)

### Copy
- Sentence case on all titles, headings, and CTAs
- CTAs are verbs: "Confirm booking" not "Confirmation"
- Helper text explains format, not the label: "With area code, e.g. +1 555-1234" not "Enter your phone number"

---

## Absolute Bans

Name each violation and know the fix.

**1. Unnecessary endpoint**
Endpoint where all data is known at send time. Adds server complexity and latency for no gain.
→ Remove endpoint; inject data via the API call payload; switch to static register.

**2. Overloaded screen**
More than 1 task per screen, or more than 8 input components on a single screen.
→ Split into multiple screens; one task, one goal per screen.

**3. Blind field**
Required field (TextInput, TextArea, DatePicker) with no `helper-text` to explain the expected format.
→ Add `helper-text` with a concrete example ("e.g. 01/01/1990", "Numbers only").

**4. Missing terminal**
No screen with `terminal: true`, or terminal screen's Footer uses `navigate` instead of `complete`.
→ Add a confirmation screen with `terminal: true` and Footer `"name": "complete"`.

**5. Binding on static flow**
Dynamic binding `${data.x}` on a static flow with no server to provide values.
→ Either remove the binding and use a literal value, or switch to endpoint register.

**6. Wrong component**
TextInput for long-form text; RadioButtonsGroup for 8+ options; re-echoing server data in the completion payload.
→ TextInput → TextArea for long text. RadioButtonsGroup → Dropdown for 8+ options. Strip server data from completion payload.

---

## Commands

| Command | Category | Description | Reference |
|---|---|---|---|
| `interview` | Preflight | Gather language, register, flow purpose, screens brief, UX context | `reference/interview.md` |
| `build` | Build | Generate complete Flow JSON from confirmed brief | `reference/build.md` |
| `validate` | Quality | Run official validator; fallback to structural checks if binary absent | `reference/validate.md` |
| `audit` | Quality | Score flow 0–20 across structure, UX, errors, performance, best practices | `reference/audit.md` |
| `debug` | Fix | Diagnose broken or unexpected flow behavior by symptom → category → fix | `reference/debug.md` |

**Deferred to v2:** `copy` (UX writing review), `endpoint` (server code generation), `send` (API integration), `critique` (scored UX review with personas).

---

## Routing rules

**No argument** → show the command table above, grouped by category.

**First token matches a command** → load `reference/<command>.md` and follow its instructions. Also load `references/flow-json-reference.md` when the command is `build` or `validate`.

**Unrecognised input** → apply Shared Flow Laws + handle the request using context from `references/flow-json-reference.md`. If the request is clearly about building a flow, run `interview` first unless context is already established.

---

## Reference files

Runtime references loaded by commands:

| File | Used by |
|---|---|
| `reference/interview.md` | `interview` |
| `reference/build.md` | `build` |
| `reference/validate.md` | `validate` |
| `reference/audit.md` | `audit` |
| `reference/debug.md` | `debug` |
| `reference/ux-patterns.md` | `audit`, `build`, unrecognised UX questions |
| `references/flow-json-reference.md` | `build`, `validate`, `debug` (source of truth) |

Source material (not loaded at runtime — for developer reference):

- `docs/` — full Meta documentation (crawled, Wayback-corrected)
- `docs/reference/components.md` — all component specs
- `docs/reference/error-codes.md` — full error code list
- `docs/guides/` — Meta implementation guides

---

## Validator

The official Meta validator (`scripts/WAFlowJSONValidator_bundle.js`, with legacy fallback to `scripts/WAFlowJSONValidator.js`) catches semantic errors that structural checks miss. Always attempt to run it. If neither file is present, run structural checks and note the limitation.

How to obtain the bundle: `scripts/README.md`.

`validate` handles the absent-bundle case gracefully — it does not block delivery.
