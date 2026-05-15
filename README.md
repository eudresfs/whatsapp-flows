# whatsapp-flows

Build, validate, audit and debug WhatsApp Flows JSON. 1 skill, 5 commands, a register split, and named anti-patterns for flows that actually work.

## Why this skill?

The official Meta docs cover the spec. They don't cover:

- Which components to use and when (and which are wrong for the job)
- Why flows get abandoned and how to structure against that
- The validator-corrected rules that diverge from the official documentation
- The difference between static and endpoint-powered flows, and when to use each
- The named anti-patterns that produce broken or low-quality flows

This skill covers all of it — from requirements gathering to a validated, audited JSON ready to publish.

## Commands

| Command | What it does |
|---|---|
| `/whatsapp-flows interview` | Gather context: language, register (static/endpoint), flow purpose, screens, UX risks |
| `/whatsapp-flows build` | Generate complete, valid Flow JSON from interview brief |
| `/whatsapp-flows validate` | Run the official Meta validator; graceful fallback to structural checks if binary is absent |
| `/whatsapp-flows audit` | Score the flow 0–20 across structure, UX, error handling, performance, best practices |
| `/whatsapp-flows debug` | Diagnose broken or unexpected behavior by symptom → category → fix |

Or use `/whatsapp-flows` directly with a description:

```
/whatsapp-flows build a 3-screen appointment booking flow
/whatsapp-flows debug my navigation payload isn't reaching the next screen
/whatsapp-flows audit <paste flow json>
```

## Register split

Every flow is either **static** or **endpoint-powered**. The skill determines this in `interview` and applies different rules downstream.

**static** — all data known at send time; no server; `navigate`/`complete` only.
**endpoint** — server required; `data_exchange`; conditional routing; encryption.

The rule: use static whenever possible. Only add an endpoint when a screen genuinely needs live data.

## The 6 absolute bans

1. **Endpoint desnecessário** — endpoint where static would suffice → remove server, inject at send time
2. **Screen sobrecarregada** — >1 task or >8 components per screen → split screens
3. **Campo cego** — required field with no `helper-text` → add format example
4. **Flow sem terminal** — no `terminal: true` screen → add confirmation screen
5. **Binding em flow static** — `${data.x}` with no endpoint → use literal or switch to endpoint
6. **Componente errado** — TextInput for long text, RadioButtonsGroup for 8+ options → use TextArea, Dropdown

## Installation

### Claude Code

```bash
claude mcp install github:eudresfs/whatsapp-flows
```

Or clone and install locally:

```bash
git clone https://github.com/eudresfs/whatsapp-flows
# Copy .claude/skills/whatsapp-flows/ into your project's .claude/skills/
```

### Other AI tools

- **Cursor**: use `.cursor/skills/whatsapp-flows/`
- **Codex / Agents SDK**: use `.agents/skills/whatsapp-flows/`
- **Gemini CLI**: use `.gemini/skills/whatsapp-flows/`

## Validator

The official Meta Flow JSON validator (`WAFlowJSONValidator.js`) catches semantic errors that structural checks miss. It is not included in this repo (proprietary binary extracted from Meta's Flow Builder).

To obtain it: see [`scripts/README.md`](scripts/README.md).

Without the binary, `validate` runs structural checks and reports the limitation clearly. All other commands work normally.

## Structure

```
whatsapp-flows/
├── SKILL.md                          # Skill definition — gates, register split, bans, commands
├── .claude/skills/whatsapp-flows/
│   ├── reference/
│   │   ├── interview.md              # Preflight questions (technical + UX)
│   │   ├── build.md                  # JSON generation — checklists, rules, examples
│   │   ├── validate.md               # Validator usage + structural fallback
│   │   ├── audit.md                  # 5-dimension scoring rubric
│   │   ├── debug.md                  # 7 symptom categories with diagnosis paths
│   │   └── ux-patterns.md            # WhatsApp-specific UX heuristics
│   └── scripts/
│       └── load-context.mjs          # Persists language + register to .whatsapp-flows-config
├── references/
│   └── flow-json-reference.md        # Validator-corrected Flow JSON spec (source of truth)
├── docs/                             # Crawled Meta documentation (source material)
├── scripts/                          # Validator runner + doc extraction tools
└── evals/                            # Evaluation test cases
```

## Reference

The skill's source of truth is [`references/flow-json-reference.md`](references/flow-json-reference.md) — a validator-corrected spec that documents where the official Meta documentation is wrong (CalendarPicker range shape, init-value context rules, array schema structure, and more).

## License

MIT
