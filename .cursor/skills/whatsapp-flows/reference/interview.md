# interview

Gather the context needed to build a valid, well-designed WhatsApp Flow. Run before `build`.

---

## What interview does

Asks the developer a structured set of questions across two layers:

1. **Technical layer** — determines the JSON shape (screens, endpoint, data model, routing)
2. **UX layer** — determines design quality (user mental model, risk of abandonment, sensitive data, trust signals)

The output is a **flow brief** that `build` consumes. Do not start generating JSON before the brief is complete.

---

## Language gate

Before any other question, check the config:

```bash
node .claude/skills/whatsapp-flows/scripts/load-context.mjs
```

If `languageSet` is false, ask:

> "Which language do you want to work in? (PT-BR / EN)"

Persist the answer:

```bash
node .claude/skills/whatsapp-flows/scripts/load-context.mjs --set-language pt-BR
```

Do not re-ask in subsequent commands in the same project.

---

## Register gate

If `registerSet` is false, determine the register as part of the interview.

**static** — no server involved; all data injected at send time; `navigate`/`complete` actions only.
**endpoint** — server required; `data_exchange` action; conditional `routing_model`; encryption; latency budget matters.

Decision rule: if ANY screen needs live data (availability, pricing, personalised content, validation) → endpoint. If all data is known at send time → static.

Persist:

```bash
node .claude/skills/whatsapp-flows/scripts/load-context.mjs --set-register static
```

---

## Technical questions (always ask if not already clear)

1. **Purpose** — What task does the user complete in this flow? One sentence.
2. **Screens** — How many screens? What happens on each? (collect data / show info / choose option / confirm)
3. **Navigation** — What is the intended screen order? Are there branches?
4. **Endpoint** — Does any screen need live server data? (→ determines register)
5. **Data model** — What data does each screen receive from the server (if endpoint)? What does each screen send forward via payload?
6. **Terminal screen** — Which screen closes the flow? What does it confirm/show?
7. **Completion payload** — What data needs to reach the business after the user submits?

---

## UX questions (ask when not implied by context)

8. **User context** — Does the user already know why they received this message? Or does the first screen need to explain context?
9. **Abandonment risk** — Is the flow long (>3 screens)? Is there a point where users might give up? What happens to partial data?
10. **Sensitive data** — Are any fields collecting passwords, ID numbers, health data, financial info? (→ `sensitive: true` on screen, `input-type: password/passcode` on field)
11. **Login requirement** — Does the user need to authenticate? If yes: can it be deferred to a late screen? (users are more motivated after seeing value)
12. **Trust signals** — Does the business logo appear in the footer? Is there a "contact us" fallback for errors?

---

## Brief format

Produce a structured brief before `build`. Use this shape:

```
FLOW BRIEF
──────────
Language:   pt-BR
Register:   static | endpoint

Purpose:    [one-sentence description]
Screens:    [list: ID → title → task]
Navigation: [sequence + branches if any]
Terminal:   [which screen, what it confirms]
Completion: [what data reaches the business]

Data model (endpoint only):
  [screen] ← receives: [fields]
  [screen] → sends: [fields]

UX notes:
  - User context: [needs intro / already knows]
  - Abandonment risk: [low / medium: mitigation]
  - Sensitive fields: [none / list]
  - Login: [none / deferred to screen N]
```

Show the brief to the developer and ask for confirmation before proceeding to `build`.

---

## Conditional questions

Ask only if the brief is ambiguous:

- Single or multiple selection? (→ RadioButtonsGroup vs CheckboxGroup vs Dropdown)
- Date, date range, or calendar visual? (→ DatePicker vs CalendarPicker single vs range)
- Long-form text? (→ TextArea, not TextInput)
- Many options (8+)? (→ Dropdown, not RadioButtonsGroup)
- Tags / multi-filter? (→ ChipsSelector v6.3+)
- Media upload needed? (→ PhotoPicker / DocumentPicker)
- Navigation list with images? (→ NavigationList v6.2+)
