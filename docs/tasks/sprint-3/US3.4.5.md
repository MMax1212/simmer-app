---
id: US3.4.5
story: US3.4
sprint: 3
assignee: Benjamin Ong
estimate_hours: 3
---

# Write Automated Integration Tests for Bookmarking and Saved Posts

## Description
Serves **US3.4** (*Bookmark / Save Posts*). This task adds automated Pytest integration tests verifying bookmark toggling, per-user isolation, and cascade deletion when a post is deleted.

## Specs
- **Test Fixture (`backend/tests/conftest.py`):**
  - Add `create_test_post(db, author_id, caption, image_url)` helper for seeded post creation.
- **Integration Tests (`backend/tests/test_Bookmark.py`):**
  - `test_bookmark_toggle`: Verifies an authenticated user can bookmark and unbookmark the same post sequentially via `POST /api/v1/posts/{post_id}/bookmark`.
  - `test_User_Isolation`: Verifies that one user's saved posts do not appear in another user's `GET /api/v1/users/me/saved-posts` response.
  - `test_deleted_post_handling`: Verifies that deleting a post automatically cascades and removes it from saved posts.

## Requirements
- Use existing Pytest `client` and `db_session` fixtures in `backend/tests/conftest.py`.
- Ensure all new and existing backend tests pass cleanly.

## Acceptance criteria
1. `create_test_post` helper is available in `backend/tests/conftest.py`.
2. `backend/tests/test_Bookmark.py` passes all 3 integration tests (`test_bookmark_toggle`, `test_User_Isolation`, `test_deleted_post_handling`).
3. Full backend and frontend test suites pass with zero regressions.
