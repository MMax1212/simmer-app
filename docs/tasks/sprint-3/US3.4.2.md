---
id: US3.4.2
story: US3.4
sprint: 3
assignee: Benjamin Ong
estimate_hours: 4
---

# Implement Backend REST API Endpoints for Bookmark Toggle and Saved Posts

## Description
Serves **US3.4** (*Bookmark / Save Posts*). With the `saved_posts` schema established in Task 3.4.1, this task implements the authenticated backend REST endpoints to toggle bookmarks on a post and retrieve the current user's saved posts collection.

Database schema creation (Task 3.4.1), frontend UI (Tasks 3.4.3 and 3.4.4), and automated test suite (Task 3.4.5) are covered in separate tasks.

## Specs
- **Toggle Bookmark (`POST /api/v1/posts/{post_id}/bookmark` in `backend/app/api/posts.py`):**
  - Requires authenticated user (`user: CurrentUser`).
  - Validates that the target post exists (returns HTTP `404` if not found).
  - Idempotently toggles bookmark state: creates a `SavedPost` record if not bookmarked, or deletes it if already bookmarked.
  - Returns `{"bookmarked": bool, "bookmark": bool}`.
- **List Saved Posts (`GET /api/v1/users/me/saved-posts` in `backend/app/api/users.py`):**
  - Requires authenticated user (`user: CurrentUser`).
  - Joins `SavedPost` for `user.id` and orders results by `SavedPost.created_at.desc()` (newest saved first).
  - Registered before `/{username}` to prevent path parameter routing collisions.
  - Enforces strict user isolation so users only see their own saved posts.

## Requirements
- Enforce authentication via `CurrentUser` dependency (HTTP `401` when unauthenticated).
- Return standard FastAPI HTTP status codes (`200`, `401`, `404`).
- Keep existing post and user endpoints unaffected.

## Acceptance criteria
1. `POST /api/v1/posts/{post_id}/bookmark` bookmarks an unbookmarked post and unbookmarks an already-bookmarked post.
2. `POST /api/v1/posts/{post_id}/bookmark` returns `404` for a non-existent post and `401` when unauthenticated.
3. `GET /api/v1/users/me/saved-posts` returns only the authenticated user's saved posts ordered newest-saved first.
4. `GET /api/v1/users/me/saved-posts` does not collide with `GET /api/v1/users/{username}`.
