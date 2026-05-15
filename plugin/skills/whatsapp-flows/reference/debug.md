# debug

Diagnose broken or unexpected WhatsApp Flow behavior.

---

## Protocol

1. Identify the **symptom** from the user
2. Map to a **category**
3. Run the **diagnostic checks** for that category
4. Propose and apply the **fix**
5. Confirm with `validate`

---

## Category map

| Symptom | Category |
|---|---|
| Flow Builder rejects the JSON | Structural |
| Flow opens but shows wrong content | Data binding |
| User fills form but data doesn't reach next screen | Payload |
| Server is never called | Endpoint routing |
| Flow doesn't send via API | API integration |
| Screen doesn't appear / navigation skips | Routing |
| Unexpected behavior on device | Runtime / device |
| Flow opens with empty fields that should be pre-filled | Init values |

---

## Category: Structural

**Symptom:** Flow Builder shows validation errors or rejects the JSON entirely.

**Checks:**
1. Is `version` a string (`"7.3"`) not a number (`7.3`)? → must be string
2. Does every screen have `title`?
3. Do screen `id` values contain only letters and underscores? (no digits, no hyphens)
4. Is there exactly one `terminal: true` screen?
5. Does that terminal screen's Footer use `"name": "complete"` not `"name": "navigate"`?
6. Is there at most 1 `Form` per screen? At most 1 `Footer`?
7. Is `Footer` the last child inside `Form` (not outside it, not before another component)?
8. Is `routing_model` absent on static flows? Present on endpoint flows?

Run `validate` — it will give exact paths for structural violations.

---

## Category: Data binding

**Symptom:** Text shows `${data.nome}` literally, or screen shows wrong value.

**Checks:**
1. Is the field declared in the screen's `data` object with the correct type?
2. Does the `data` field have `__example__` (required by validator; also needed for rendering in Builder)?
3. Is the binding syntax correct? Simple refs: `"${data.campo}"` — no backticks. Expressions with text: `` "`'Label: ' ${data.campo}`" ``
4. For endpoint flows: is the server returning the field in the response JSON with the correct key?
5. For static flows: is the field being injected in the send-flow API call payload?

---

## Category: Payload (data not reaching next screen)

**Symptom:** Next screen doesn't receive data the user entered; fields appear empty.

**Checks:**
1. Does the navigate `payload` include the field? `"${form.field_name}"` (field name must match the `name` attribute of the component)
2. Does the destination screen's `data` declare this field with matching key, type, and `__example__`?
3. Is the component inside a `Form`? Components outside a Form are not accessible via `${form.campo}`.
4. For CalendarPicker range: is the payload using `${form.picker.start-date}` and `${form.picker.end-date}` separately?
5. Are `init-values` (plural, on Form) vs `init-value` (singular, on component) used correctly?

---

## Category: Endpoint routing

**Symptom:** `data_exchange` action fires but server is never called; or wrong screen is shown after exchange.

**Checks:**
1. Is `routing_model` present? Does it list every screen ID that can be navigated to?
2. Is `data_api_version` present alongside `routing_model`?
3. Does the `data_exchange` action have a `payload` with the correct fields?
4. Is the server's response JSON returning `"version"` and `"screen"` fields? (Required for routing)
5. Is the endpoint URL correct in the Flow's configuration in Meta Business Manager?
6. Is the WACS encryption/decryption working? (Check server logs for decryption errors)

---

## Category: API integration

**Symptom:** Flow message fails to send; API returns an error.

**Checks:**
1. Is `flow_id` a valid, published flow (not a draft)?
2. Is `flow_token` present and not expired?
3. Is `flow_action` set correctly (`"navigate"` for flows that start at a specific screen; `"data_exchange"` for endpoint flows)?
4. Is the message type `"interactive"` with `"type": "flow"`?
5. Are `to` and `messaging_product` set?
6. For endpoint flows: is the initial data for the first screen included in `flow_action_payload.data`?

Reference: `docs/guides/sending-a-flow.md`

---

## Category: Routing / screen not appearing

**Symptom:** Navigation skips a screen, shows wrong screen, or flow ends prematurely.

**Checks:**
1. Are screen IDs referenced in `navigate` exactly matching the declared `id` fields? (Case-sensitive)
2. Is there a conditional `Switch` that might be routing to an empty case?
3. Is the `routing_model` (endpoint flows) returning the correct `"screen"` value?
4. Is there a screen with no path leading to it (orphaned)?

---

## Category: Init values

**Symptom:** Fields that should be pre-filled appear empty when flow opens.

**Checks:**
1. For static flows: is the field present in `flow_action_payload.data` in the send-flow API call?
2. Is the screen `data` schema declaring the field as the correct type?
3. Inside Form: using `init-values` (plural) on the `Form` element, not `init-value` on the component
4. Outside Form: using `init-value` (singular) on the component
5. For DatePicker/CalendarPicker: is `init-value` format `"YYYY-MM-DD"`? Empty string `""` is invalid.

---

## Category: Runtime / device

**Symptom:** Flow works in Builder preview but behaves differently on a real device.

**Checks:**
1. Check the WhatsApp version on the device — some components require minimum versions (CalendarPicker: v6.1+, NavigationList: v6.2+, ChipsSelector: v6.3+, ImageCarousel: v7.1+)
2. Check flow JSON version vs device WhatsApp version compatibility (`docs/reference/versioning.md`)
3. For image data-source: are images under 100KB? Larger images silently fail on some devices.
4. Is the flow published (not draft)? Preview mode has different behavior.
5. For endpoint flows: is the server responding within 10 seconds? Timeout causes the flow to show an error state.

---

## Delivering the diagnosis

Structure:
1. **Identified category** — what type of problem this is
2. **Root cause** — the specific misconfiguration found
3. **Fix** — exact change to make in the JSON
4. **Verification** — re-run `validate` and/or test in Flow Builder

If multiple categories match the symptom, check the most likely one first (Structural → Payload → Endpoint routing).
