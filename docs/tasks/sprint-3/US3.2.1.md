---
id: US3.2.1
story: US3.2
sprint: 3
assignee: Ulises Diaz
estimate_hours: 3
---

# Author-protected post update and deletion endpoints

Assignment source: Sprint 3 Plan, Section 6. This task does not implement edit menus or editing modals.

## Contract

- `PUT /api/v1/posts/{id}` returns 200 with PostResponse. It replaces the editable post representation: caption and image_url required; media_type defaults to image; recipe_id defaults to null. Clients preserving a recipe/media type must send those fields.
- Captions: 1–2000 characters, not whitespace-only. Media locations: 1–1000 characters, not whitespace-only. Keep existing creation semantics accepting URL/path/data strings; do not impose a new URL-only contract.
- Unknown fields (including author_id/id) are rejected with 422. Author identity and created_at are immutable.
- A non-null recipe_id must exist; otherwise 404 before any changes are made. A null/omitted recipe_id detaches a linked recipe. updated_at advances on a successful replacement.
- `DELETE /api/v1/posts/{id}` returns an empty 204 response. Subsequent reads return 404. Likes, comments and bookmarks are removed through existing cascades; linked recipes and users are preserved.
- Both routes require authentication (401); authenticated non-authors receive 403, including admins. Missing posts return 404. No admin override is introduced by this task.

## Test-first verification

The initial 20 cases in tests/test_US3_2_1.py were run before implementation: 20 failed because PUT/DELETE returned 405. Tests cover successful persistence and deletion, invalid-body atomicity, missing resources, authentication, cross-user/admin denial, and populated cascade cleanup.

Existing test fixtures use isolated databases; no user database is changed by the tests.
