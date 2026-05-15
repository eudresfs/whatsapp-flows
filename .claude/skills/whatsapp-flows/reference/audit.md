# audit

Score a WhatsApp Flow across 5 quality dimensions. Produces actionable findings tagged by severity.

---

## When to run

After `validate` confirms the flow is structurally valid. `audit` checks quality, not correctness.

---

## Scoring

5 dimensions × 4 points each = **20 points total**.

| Score | Meaning |
|---|---|
| 4 | Excellent — no issues |
| 3 | Good — minor gaps |
| 2 | Acceptable — improvements needed |
| 1 | Poor — significant problems |
| 0 | Critical failure — blocks publishing |

Severity tags: **P0** (critical, must fix), **P1** (important), **P2** (nice to have).

---

## Dimension 1 — JSON Structure (0–4)

Check:
- Version is current (7.x preferred; penalise if <5.0 without justification) [–1 if <5.0]
- `terminal: true` screen exists and is reachable [–2 if absent]
- All screen IDs use only letters and underscores [–1 per violation]
- `routing_model` complete when endpoint used (all routes covered) [–1 if incomplete]
- No orphaned screens [–1 per screen]
- `__example__` present on all `data` fields [–1 if missing on critical fields]

**Score 4** if none of the above apply. Deduct per finding.

---

## Dimension 2 — UX / Cognitive Load (0–4)

Check:
- Each screen has exactly 1 task (a single goal the user completes) [–1 per screen with >1 task]
- Screen component count ≤ 8 (excluding Footer) [–1 per screen exceeding]
- Screen titles are action-oriented and concise (≤ 5 words) [–0.5 per weak title]
- Multi-step flows (>3 screens) show progress in screen titles (e.g. "Passo 1 de 3") [–1 if absent]
- Terminal screen confirms the completed action (not just "Done") [–1 if vague]
- CTAs match the action: "Confirmar agora" not "Enviar", "OK" or generic strings [–1 per weak CTA]
- Completion payload does not include base64 images [–1 if found]
- Login screen (if any) appears late in the flow, after showing value [–1 if too early]

**Score 4** if all apply. Deduct per finding.

---

## Dimension 3 — Error Handling (0–4)

Check:
- Every required TextInput/TextArea has `helper-text` explaining format [–1 per missing]
- `flow_token` expiry strategy is documented (in comments or endpoint spec) [–1 if unaddressed]
- Sensitive fields use `input-type: "password"` or `"passcode"` and screen has `sensitive: true` [–2 per violation]
- Error recovery path exists: if endpoint call fails, user is redirected, not stranded [–1 if absent for endpoint flows]
- Password/passcode fields absent from completion payload [–1 if found]

**Score 4** if all apply. Deduct per finding.

---

## Dimension 4 — Performance / Efficiency (0–4)

Check:
- Endpoint used only where live data is necessary; static elsewhere [–2 if endpoint is unnecessary]
- First screen of endpoint flow is static (no `data_exchange`) to optimise opening [–1 if not]
- Completion payload contains only user-inputted data (not server data re-echoed back) [–1 if bloated]
- Screen count is minimal for the task (no screens that only show static text reachable via a button) [–1 per redundant screen]
- `data-source` images ≤ 100KB (v6.0+) [–1 per violation]

**Score 4** if all apply. Deduct per finding.

---

## Dimension 5 — Meta Best Practices (0–4)

Check:
- No absolute bans violated (see Shared Flow Laws in SKILL.md) [–2 per ban]
- Component used matches the use case (TextArea for long text, Dropdown for 8+ options) [–1 per mismatch]
- CalendarPicker range payload uses `start-date`/`end-date` separately (not full object) [–1 if wrong]
- `Switch` `"default"` case present [–1 if missing]
- Backtick expressions with static text use single quotes inside [–1 per violation]
- Flow does not collect data beyond what is needed for the stated purpose [–1 if over-collecting]

**Score 4** if all apply. Deduct per finding.

---

## Output format

```
FLOW AUDIT
──────────
Total: XX / 20

Dimension 1 — Structure:      X/4
Dimension 2 — UX/Cognitive:   X/4
Dimension 3 — Error Handling: X/4
Dimension 4 — Performance:    X/4
Dimension 5 — Best Practices: X/4

Findings:
P0 [Dimension] Screen/location — Issue — Suggested fix
P1 [Dimension] Screen/location — Issue — Suggested fix
P2 [Dimension] Screen/location — Issue — Suggested fix

Next step: [suggested command based on findings]
```

**Next step logic:**
- P0 structural issues → `build` (regenerate) or `debug`
- P0 UX issues → re-interview + `build`
- Only P1/P2 findings → `validate` + share with user
- Score ≥ 16, no P0 → flow is publishable; note P1/P2 as improvements
