# ux-patterns

WhatsApp Flows UX heuristics. These are not in the official Meta docs. They come from behavioral patterns specific to conversational UI and the WhatsApp context.

This file grows as empirical knowledge accumulates. Current content reflects documented best practices and the conversational context of WhatsApp.

---

## The WhatsApp context

Users open flows inside a chat. They are in a conversational mindset — not a web app mindset. This has consequences:

- Flows feel slow if they have too many screens. A user who needs 3 minutes to complete will often abandon.
- Trust is lower than on a website. The user doesn't know if this is the real business or a scam. Trust signals matter more here.
- Back navigation is unexpected. Many users don't know they can go back, so flows should minimise the need to.
- WhatsApp is used on mobile, often in fragmented attention contexts (commuting, waiting in line). Forms need to be short and clear.

---

## Screen design principles

### One task per screen

Each screen should have one thing the user does or decides. If a screen mixes "enter personal data" with "choose a plan", split it.

Cognitive overload causes abandonment. It also makes error handling harder — when a submit fails, it's unclear which field caused the problem.

### Screen titles orient, CTAs commit

Screen title: tells the user where they are. Short, action-framed. "Personal info", "Choose a plan", "Confirmation".

CTA (Footer label): commits the user to the next action. Make it specific. "Confirm booking" beats "Continue". "Submit" beats "OK".

### Progress indication for long flows

If the flow has more than 3 screens and users don't know it, they'll abandon thinking it's endless.

Options:
- Screen titles: "Step 1 of 3 — Your info"
- A `TextSubheading` component at the top of each screen: "Step 2 of 4"

### Terminal screen must confirm

The terminal screen is the user's receipt. It must:
1. Confirm what was done ("Your appointment has been confirmed")
2. Set expectations for next steps ("You'll receive a confirmation message shortly")
3. Provide a trust anchor (business logo in footer is automatic; optionally add support CTA via EmbeddedLink)

Generic terminals ("Obrigado!") create anxiety. The user doesn't know if the action was saved.

---

## Copy principles for WhatsApp Flows

### Sentence case everywhere

Screen titles, headings, CTAs, helper text — all sentence case. No ALL CAPS. No Title Case For Every Word.

✓ "Confirm booking"
✗ "CONFIRM BOOKING"
✗ "Confirm Booking"

### CTAs are verbs, not nouns

✓ "Confirm" / "Choose plan" / "Submit"
✗ "Confirmation" / "Plan" / "Submission"

### Helper text explains format, not the label

The label already says what the field is. Helper text says how to fill it.

Label: "Phone"
Helper text: "With area code, e.g. +1 555-1234"

Not:
Helper text: "Enter your phone number" ← redundant

### Error messages are human

Validator error messages in the JSON are shown to users when validation fails client-side.

✓ "Enter a valid email, e.g. name@email.com"
✗ "Email format invalid"
✗ "Invalid field"

---

## Trust and abandonment

### Deferred login

If the flow requires login/authentication, put it as late as possible. Show the value first. Users who understand what they'll get are more willing to authenticate.

Bad: Screen 1 = login, Screen 2 = value
Good: Screen 1 = value preview, Screen 2 = personalise, Screen 3 = login to confirm

### Sensitive field labeling

When collecting sensitive data (CPF, passwords, health info):
- Use `input-type: "passcode"` or `"password"` — these mask input
- Mark the screen `"sensitive": true` — excludes it from the flow response summary
- Explicitly tell the user why you need it: add helper text explaining purpose

### Support escape hatch

Long or complex flows should have a way for the user to reach support if confused. Use `EmbeddedLink` or `OptIn` with a "Need help?" link as a secondary action before the main CTA.

---

## Component selection heuristics (UX layer)

Beyond technical correctness, component choice affects perceived quality:

**RadioButtonsGroup vs Dropdown:**
RadioButtons display all options simultaneously — good for 2–4 when comparison matters. Dropdown hides options behind a tap — good for 5+ to reduce visual noise. Never use RadioButtons for 8+ items; the screen becomes a wall of text.

**ChipsSelector vs CheckboxGroup:**
Both allow multiple selection. ChipsSelector feels lighter and more tag-like — good for interests, filters, preferences. CheckboxGroup feels more formal — good for agreements, terms, confirmation of items.

**DatePicker vs CalendarPicker:**
DatePicker is compact text-based input — good when the date is well-known (birth date, document expiry). CalendarPicker renders a visual calendar — good when the user is choosing a date they don't have memorised (appointments, travel, reservations).

**NavigationList:**
Use when items are distinct entities that lead to different screens (product categories, service types). Not for lists of choices within a form — use RadioButtons or Dropdown for that.

---

## Flow length guidelines

| Flow length | Risk | Mitigation |
|---|---|---|
| 1–2 screens | None | — |
| 3–4 screens | Low | Clear progress indication |
| 5–6 screens | Medium | Minimise optional steps; save partial data via endpoint |
| 7+ screens | High | Re-evaluate scope; consider splitting into two flows |

The 10-second endpoint timeout applies per request. Long flows with multiple endpoint calls must each resolve within 10 seconds independently.

---

## What not to do (named patterns)

**The form dump** — putting all fields for a multi-step process on a single screen to "keep it short". One screen, 10 fields. Users abandon before completing. Fix: split by logical grouping, one task per screen.

**The silent terminal** — terminal screen says "Enviado!" with no detail. User doesn't know what was sent, to whom, or what happens next. Fix: confirm the specific action and set expectations.

**The deep endpoint** — using `data_exchange` on every screen of a simple registration flow because "we might need server data later". Endpoint adds latency and complexity. Fix: use static where possible; only add endpoint for screens that actually need live data.

**The bare required field** — required TextInput or TextArea with no `helper-text`. Users discover the format rules only after submitting and getting an error. Fix: always add `helper-text` to required fields.

**The early gate** — asking for login or account creation as the first or second screen. Users haven't seen value yet. Fix: defer login to the last step before completion.
