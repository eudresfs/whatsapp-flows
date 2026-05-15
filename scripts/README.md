# scripts/

## run_validator.js

Node.js shim that loads Meta's official Flow JSON validator and exposes a CLI interface.

```bash
node run_validator.js <flow.json> [version]
```

Requires `WAFlowJSONValidator.js` in the same directory. See below.

---

## WAFlowJSONValidator.js — how to obtain

This file is Meta's bundled validator, extracted from the Flow Builder web app. It is **not included** in this repository (proprietary).

### Extraction steps

1. Open [https://business.facebook.com/wa/manage/flows/](https://business.facebook.com/wa/manage/flows/) in Chrome (must be logged in)
2. Open DevTools → **Sources** tab → **Search** (Ctrl+Shift+F / Cmd+Opt+F)
3. Search for: `WAFlowJSONValidator`
4. Open the file that contains it (usually a large minified bundle)
5. In the Sources panel, right-click the file → **Save as** or copy the full content
6. Find the `WAFlowJSONValidator` export within the bundle — it will be wrapped in Meta's `__d()` module format
7. Copy the full `__d("WAFlowJSONValidator", ...)` block
8. Save as `scripts/WAFlowJSONValidator.js`

If the path in `run_validator.js` is incorrect, update the `VALIDATOR_PATH` constant at the top of that file.

### Fallback

If the binary is unavailable, `validate` command runs structural checks only (screen IDs, terminal screen, routing_model presence, component limits). These catch the most common errors but not all semantic rules.

---

## extract_dmc.py

Extracts documentation from Meta's DMC (Developer Meta Components) HTML payload.

```bash
python extract_dmc.py <html_file> > output.md
```

---

## html_to_md.py

Converts Wayback Machine archived HTML of Meta docs to Markdown.

```bash
python html_to_md.py
```

Output goes to `../docs/reference/`.
