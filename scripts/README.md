# scripts/

## run_validator.js

Node.js shim that loads Meta's official Flow JSON validator and exposes a CLI interface.

```bash
node run_validator.js <flow.json> [version]
```

Requires the validator bundle in the same directory. See below.

---

## WAFlowJSONValidator_bundle.js — how to obtain

This is Meta's full Flow Builder validator bundle (~200 `__d()` modules covering every validator chain V500 → V703). It is **not included** in this repository (proprietary code extracted from Meta's web app).

### Extraction steps

1. Open [https://business.facebook.com/wa/manage/flows/](https://business.facebook.com/wa/manage/flows/) in Chrome (must be logged in)
2. Open DevTools → **Sources** tab → **Search** (Ctrl+Shift+F / Cmd+Opt+F)
3. Search for: `WAFlowJSONValidatorChainV703`
4. Open the bundle file that contains it (usually `FlowsBuilderPageRoute.bundle...js`)
5. In the Sources panel, right-click the file → **Save as**, or copy the full content
6. Save as `scripts/WAFlowJSONValidator_bundle.js`

The runner auto-detects the bundle. No code changes required.

### Legacy single-file fallback

If you only have the older single-module extraction, save it as `scripts/WAFlowJSONValidator.js` — the runner falls back to that path when the bundle is absent.

### No-binary fallback

If neither file is available, the `validate` skill command runs structural checks only (screen IDs, terminal screen, routing_model presence, component limits). These catch common errors but miss many semantic rules.

---

## extract_v703_rules.js

Parses the validator bundle and emits a markdown reference of every rule applied to Flow JSON v7.3.

```bash
node extract_v703_rules.js
```

Writes to `references/v703-validation-rules.md`. Re-run after refreshing the bundle.

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
