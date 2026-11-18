---
id: US3.2.4
story: US3.2
sprint: 3
assignee: Ulises Diaz
estimate_hours: 4
---

# Post lifecycle API integration acceptance

Follow-on task authorized in chat. The Sprint Plan's explicit individual assignment is 3.2.1; this increment extends its test coverage instead of duplicating the existing 20 cases.

## Existing coverage reused

`tests/test_US3_2_1.py` already exercises author update/delete success, no-login rejection, other-user/admin rejection, 404 responses, blank/oversized content and unknown fields, recipe-link replacement/detachment, invalid-recipe atomicity and basic cascade cleanup. These tests originally failed before the 3.2.1 implementation and then passed.

## Added acceptance coverage

`tests/test_US3_2_4.py` adds 16 cases against a temporary SQLite file built with Alembic migrations. FK enforcement is enabled for application connections and every HTTP request receives a fresh SQLAlchemy session, preventing cached ORM state from hiding persistence defects.

- Update-read-delete lifecycle, repeated deletion, and update-after-delete behavior.
- Invalid-token and deactivated-account rejection, plus cross-user 403, without committed changes.
- Null fields, forged timestamps and incomplete PUT rejection without changing data.
- Maximum-length valid values and documented full-replacement optional defaults.
- Likes/comments/bookmarks created by a different user are removed only for the deleted post; unrelated posts and engagement survive.
- Linked recipe and author/user accounts survive post deletion.

The added cases verify existing production behavior; no new production behavior or artificial failure is introduced just to produce a red test. No user databases are used or modified. Shared dependency overrides are restored in fixture cleanup.

## Integration boundary

This increment covers the backend acceptance portion of 3.2.4. Full browser edit/delete journeys remain dependent on connecting PostActions/PostEditModal to Bryan's feed and resolving the API-client integration. Component behavior is tested separately in frontend/src/test/PostActions.test.tsx and PostEditModal.test.tsx. This document does not claim those components are already mounted in the website.

## Verification

Full backend suite after adding all 16 cases: **147 passed**, with one existing Starlette/httpx deprecation warning. No production source changes were needed. Diff whitespace validation passed. This increment adds backend acceptance coverage; full browser lifecycle acceptance remains pending feed-card integration.
