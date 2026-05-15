# build

Generate a complete, valid WhatsApp Flow JSON from the interview brief.

---

## Gate

`interview` must have produced a confirmed brief. If not, run `interview` first.

---

## Source of truth

Read `references/flow-json-reference.md` before generating. It contains validator-corrected rules that override the official Meta documentation where they conflict. Do not rely on training knowledge for component-level details.

---

## Defaults

- `"version": "7.3"` unless the user has an existing flow at a lower version and does not request an upgrade
- `SingleColumnLayout` — the only supported layout type
- `Form` wraps all input components and the `Footer` on screens that collect data
- `terminal: true` on the final screen; `Footer` on that screen uses `"name": "complete"`

---

## Register branch

### Static register

- No `routing_model`, no `data_api_version` — omit both entirely
- All data known at send time; inject via the `data` field when sending the flow message
- Only `navigate` and `complete` actions; no `data_exchange`
- Screen `data` field declares schema + `__example__` for each field

### Endpoint register

- Include `routing_model` (must cover ALL navigate destinations) and `data_api_version`
- Use `data_exchange` action for screens that need live server data
- First screen should be static (no data_exchange) to optimise flow opening latency
- Encryption required — document the WACS public key handling in your endpoint implementation
- `routing_model` with conditional routes only when needed; document each route

---

## Pre-build checklist

Work through this before running the validator. These are the most common rejection causes:

**Structure**
- [ ] Screen IDs: letters and underscores only (`COLLECT_DATA` ✓, `SCREEN_1` ✗, `SCREEN-ONE` ✗)
- [ ] Every screen has `title`
- [ ] Terminal screen has `terminal: true` and Footer with `"name": "complete"`
- [ ] Static flow: no `routing_model`, no `data_api_version`
- [ ] Endpoint flow: `routing_model` covers every `navigate` destination

**Navigation**
- [ ] `next` in navigate is an object `{"type": "screen", "name": "SCREEN_ID"}`, never a string
- [ ] Destination screen declares in `data` every field passed in `payload`
- [ ] CalendarPicker range payload sends `start-date` and `end-date` separately

**Components**
- [ ] No `input-type: "date"` on TextInput — use DatePicker
- [ ] `RadioButtonsGroup`/`Dropdown`/`CheckboxGroup`/`OptIn` have no `helper-text`
- [ ] `helper-text` only on: TextInput, TextArea, DatePicker, CalendarPicker
- [ ] `init-value`/`init-values` correct: plural inside Form, singular outside
- [ ] `min-chars`/`max-chars`/`max-length` are numbers, not strings
- [ ] Backticks with static text use single quotes: `` `'Total: ' ${data.valor}` ``
- [ ] `data-source` used (not `options`, `items`, `values`)
- [ ] Maximum 1 Form and 1 Footer per screen
- [ ] Form contains Footer as its last child
- [ ] `Switch` has a `"default"` case
- [ ] `data-source` images ≤ 100KB (v6.0+)
- [ ] Array schema in `data` uses `items.properties` structure

---

## Component selection guide

| Situation | Component |
|---|---|
| Short free text | `TextInput` (`input-type: "text"`) |
| Long free text | `TextArea` |
| Single choice, 2–4 options | `RadioButtonsGroup` |
| Single choice, 5–7 options | `RadioButtonsGroup` (acceptable) or `Dropdown` |
| Single choice, 8+ options | `Dropdown` |
| Multiple choice | `CheckboxGroup` |
| Tags / multi-filter | `ChipsSelector` (v6.3+) |
| Single date, simple | `DatePicker` |
| Single date, visual calendar | `CalendarPicker` `single` (v6.1+) |
| Date range | `CalendarPicker` `range` (v6.1+) |
| Terms acceptance | `OptIn` |
| Navigable list with image | `NavigationList` (v6.2+) |
| Photo upload | `PhotoPicker` |
| Document upload | `DocumentPicker` |
| Static image | `Image` |
| Image carousel | `ImageCarousel` (v7.1+) |
| Inline clickable link | `EmbeddedLink` |
| Primary action button | `Footer` |

---

## Critical rules (validator-confirmed)

### `init-value` context

- **Inside Form**: use `init-values`/`error-messages` (plural) on the `Form` element
- **Outside Form**: use `init-value`/`error-message` (singular) on the component

### Backtick expressions

Simple reference — no backtick needed:
```json
{ "text": "${data.email}" }
```

Expression with static text — single quotes required inside backtick:
```json
{ "text": "`'Total: R$ ' ${data.valor}`" }
```

Broken — static text without single quotes breaks the parser:
```json
{ "text": "`E-mail: ${data.email}`" }
```

### Data passing between screens

Destination screen must declare every payload field in its `data`:

```json
"payload": { "name": "${form.name}", "email": "${form.email}" }
```

```json
"data": {
  "name":  { "type": "string", "__example__": "Jane Smith" },
  "email": { "type": "string", "__example__": "jane@example.com" }
}
```

### Array schema in `data`

```json
"lista": {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id":    { "type": "string" },
      "title": { "type": "string" }
    }
  },
  "__example__": [{ "id": "1", "title": "Exemplo" }]
}
```

### CalendarPicker range — doc is wrong

The official Meta documentation contains errors for CalendarPicker range mode. Validator-confirmed correct shape:

- `label`, `helper-text` → **string** (not objects)
- `required` → **boolean** (not object)
- `error-message` → **does not exist** on CalendarPicker

Payload — send fields separately:
```json
"payload": {
  "checkin":  "${form.periodo.start-date}",
  "checkout": "${form.periodo.end-date}"
}
```

### Switch (conditional rendering)

`"default"` case is required:

```json
{
  "type": "Switch",
  "value": "${data.tipo}",
  "cases": {
    "opcao_a": [ { "type": "TextBody", "text": "Caso A" }, { "type": "Footer", "..." } ],
    "default": []
  }
}
```

---

## Canonical minimal example (static, 2 screens)

```json
{
  "version": "7.3",
  "screens": [
    {
      "id": "COLLECT",
      "title": "Your info",
      "data": {},
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          {
            "type": "Form",
            "name": "form",
            "children": [
              {
                "type": "TextInput",
                "name": "name",
                "label": "Full name",
                "input-type": "text",
                "required": true
              },
              {
                "type": "Footer",
                "label": "Continue",
                "on-click-action": {
                  "name": "navigate",
                  "next": { "type": "screen", "name": "CONFIRM" },
                  "payload": { "name": "${form.name}" }
                }
              }
            ]
          }
        ]
      }
    },
    {
      "id": "CONFIRM",
      "title": "Done!",
      "terminal": true,
      "data": {
        "name": { "type": "string", "__example__": "Jane Smith" }
      },
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          {
            "type": "Form",
            "name": "form",
            "children": [
              {
                "type": "TextBody",
                "text": "${data.name}, your registration was received."
              },
              {
                "type": "Footer",
                "label": "Close",
                "on-click-action": {
                  "name": "complete",
                  "payload": {}
                }
              }
            ]
          }
        ]
      }
    }
  ]
}
```

---

## Delivery format

Always produce two blocks:

**Block 1 — Explanation**
Prose: what was built, non-obvious decisions, which register was used and why.

**Block 2 — Full JSON**
```json
{ ...complete validated flow... }
```

Never emit fragments with `// ...rest here`. Always the full JSON.

After delivering, suggest: `validate` to run the official validator.
