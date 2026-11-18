---
id: US3.2.3
story: US3.2
sprint: 3
assignee: Ulises Diaz
estimate_hours: 3
---

# Post editing modal

Follow-on task authorized in chat after 3.2.2; Section 6 of the plan individually assigns Ulises 3.2.1, not this follow-on task.

`PostEditModal` accepts a post snapshot (id, caption, image_url, media_type, recipe_id), onCancel, and onSaved(updatedPost). The host opens it from PostActions.onEdit, closes it on cancel/success and updates its card from the returned record. The host must restrict author access; the server independently enforces it.

## Behavior

- Prefill and edit caption/media location; preserve existing media type and recipe association in full PUT requests.
- Reject blank values and enforce backend length limits. Keep the backend's URL/path/data-string compatibility.
- Cancel/Escape send no request; focus begins on Caption and remains contained, then returns to the trigger on unmount.
- Disable controls and synchronously lock during save; show API errors without losing drafts and allow retry.
- Only successful responses invoke onSaved; ignore responses after unmount. Switching post IDs resets the draft.

## TDD and scope

Seven tests failed with the empty modal before implementation. They cover prefilled values, cancellation, authenticated PUT/preserved metadata, blank input, retry, double-submit locking and keyboard behavior.

This component is not yet mounted in a production feed; integration requires the feed/post-card owner. It does not create another feed or post-authoring UI.
