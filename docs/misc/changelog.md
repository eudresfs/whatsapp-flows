# Changelog

Source: https://developers.facebook.com/docs/whatsapp/flows/changelog/

> **Crawl note — truncation:** The live page (canonical URL `https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/changelog/`) renders many additional historical entries (going back to 2023) that load via client-side JavaScript / "load more" controls. The static HTML returned to the WebFetch crawler only contained entries from **Dec 10, 2024 through Nov 11, 2025**. Multiple follow-up fetches with targeted date-range prompts (Oct 2024 → May 2024, Apr 2024 and earlier) all reported "no entries in this range present in the page content." The WebFetch summarizer also condensed bullets despite an explicit verbatim instruction, so wording below may be lightly paraphrased rather than literal HTML text. The older history must be retrieved with a JS-capable crawler / browser MCP if needed.

**Updated on:** Nov 11, 2025

---

## Nov 11, 2025

### Flows on WhatsApp Web Support

Beginning in early **December 2025**, WhatsApp will support Flows on WhatsApp Web. Users can "open, complete, and view Flow responses on WhatsApp Web companions" with no required action from businesses.

### WhatsApp Flows Endpoints Security Enhancements (Data API Version 4.0)

The platform introduced a two-signature authentication mechanism:

1. **Platform-side Signature Verification** — The system verifies authorization for flow message requests automatically (handled by Meta).
2. **Flow Token Signature** — An optional layer allowing businesses to verify request authenticity.

To enable these improvements, set `data_api_version` to `4.0` in the Flow JSON.

### Flow JSON Version 7.3

Improved Flow JSON validations for routing models and data models, making error detection easier without changing existing functionality.

---

## Sep 10, 2025

Flow version 5.0 is frozen as of September 10th, 2025. Developers should upgrade to the recommended version to avoid disruption.

### Flow JSON Validation Updates

- Improved validation for routing model and data model.
- Enhanced error detection without functional changes.

---

## Jul 8, 2025

Flow version 5.0 will freeze on September 9th, 2025.

### Flow JSON Version 7.2 Released

- Nested expressions in actions are now validated for referenced variables.
- Ensures referenced variables in the data model exist.
- Improved error detection in Flow JSON.

---

## Jun 10, 2025

### Flow JSON Version 7.1 Released

**ChipsSelector Component Updates**

- Can now be used inside `If` / `Switch` components.
- Supports `on-select-action` and `on-unselect-action` properties.

**Image Carousel Component**

- New component allowing users to slide through multiple images.

---

## Apr 8, 2025

Flow versions 2.1, 3.0, 3.1, and 4.0 are now frozen (as of April 8th, 2025).

### Message Template Updates

Flows can now be sent "with other types of buttons as part of the same message." Icon selection is available for Flow types.

---

## Mar 11, 2025

### Flow JSON Version 7.0 Released

**TextArea and TextInput Updates**

- New `label-variant: 'large'` attribute for positioning labels above input fields.

**on-select-action Behavior Reverted**

- No longer triggers when a new screen renders (reverts the version 6.0 change). Behavior returns to pre-6.0 functionality where component-level `on-select-action`s don't trigger on screen render.

**Form Validations**

- Type checking introduced for `init-values` and `error-messages` properties.

---

## Jan 14, 2025

### Flow JSON Version 6.3 Released

**Chips Selector Component**

- Presents options in a compact, interactive format for preference selection (e.g. preferences or time slots).

**RichText with Footer Support**

- RichText component now works with the Footer component on the same screen.

**Developer Tooling Improvements**

- Published Flow creation in a single API call with optional `flow_json` and `publish` parameters.
- Simplified Send Flow API — requires only `flow_message_version`, `flow_cta`, and `flow_id` / `flow_name`.
- Simplified message template creation with Flow button — requires only `text` and the flow identifier.

---

## Dec 10, 2024

### Flow JSON Version 6.2 Released

**NavigationList Component**

- User-friendly exploration of multiple options within a Flow with support for text, images, and tags.

---

<!--
End of entries available in the static page snapshot.
Older entries (Nov 2024 and earlier, back to 2023) are present on the live page
but were not returned by the static crawler — see "Crawl note" at the top.
-->
