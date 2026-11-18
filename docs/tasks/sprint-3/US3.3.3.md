---
id: US3.3.3
story: US3.3
sprint: 3
assignee: Maximo Mora
estimate_hours: 4
---

# Build Backend Endpoints for Creating, Listing, and Deleting Post Comments

## Description
Serves **US3.3** (*Likes & Comments on Community Posts*). With the `PostComment` database model and table established in US3.3.1 and the frontend `CommentDrawer` component created in US3.3.5, Simmer requires the backend REST API endpoints to support full comment lifecycle operations under community posts.

This task implements:
1. `GET /api/v1/posts/{post_id}/comments` — Retrieve all comments for a community post in chronological order, with author username and avatar metadata, supporting optional `limit` and `offset` pagination.
2. `POST /api/v1/posts/{post_id}/comments` — Authenticated endpoint for posting a new comment on a post, validating content length and returning the newly created comment.
3. `DELETE /api/v1/comments/{comment_id}` (and `DELETE /api/v1/posts/{post_id}/comments/{comment_id}`) — Authenticated endpoint allowing the comment author or an admin to delete a comment.
4. Schemas in `backend/app/schemas/post.py` (`CommentCreate`, `CommentOut`).
5. Automated Pytest suite in `backend/tests/test_US3_3_3_comments.py`.

## Specs
- **Pydantic DTO Schemas (`backend/app/schemas/post.py`):**
  - `CommentCreate`:
    - `content`: `str` (min length 1, max length 1000)
  - `CommentOut`:
    - `id`: `int`
    - `post_id`: `int`
    - `user_id`: `int`
    - `username`: `str`
    - `avatar_url`: `str | None`
    - `content`: `str`
    - `created_at`: `datetime`

- **REST API Endpoints:**
  - **`GET /api/v1/posts/{post_id}/comments`**:
    - **Authentication:** Public (anyone can view comments on public posts).
    - **Query Parameters:** `limit: int = 50` (1..100), `offset: int = 0` (ge=0).
    - **Response:** `200 OK` $\rightarrow$ `list[CommentOut]` ordered by `created_at ASC` (chronological).
    - **Validation:** Returns `404 Not Found` if `post_id` does not exist.
  - **`POST /api/v1/posts/{post_id}/comments`**:
    - **Authentication:** Required (`CurrentUser` guard; returns `401 Unauthorized` if unauthenticated).
    - **Body:** `CommentCreate` (`content: str`). Content must not be empty or solely whitespace.
    - **Response:** `201 Created` $\rightarrow$ `CommentOut`.
    - **Validation:** Returns `404 Not Found` if `post_id` does not exist.
  - **`DELETE /api/v1/comments/{comment_id}`**:
    - **Authentication:** Required (`CurrentUser` guard; returns `401 Unauthorized` if unauthenticated).
    - **Response:** `204 No Content`.
    - **Authorization:** Only the author of the comment (`comment.user_id == user.id`) or an admin (`user.role == "admin"`) may delete. Other users receive `403 Forbidden` (`detail="Not authorized to delete this comment"`).
    - **Validation:** Returns `404 Not Found` if `comment_id` does not exist.

## Requirements
- Use FastAPI, SQLAlchemy 2.0 select queries, and Pydantic v2 schemas.
- Adhere strictly to the endpoint contract defined in `docs/sprint3/spec.md` and frontend `frontend/src/services/api.ts`.
- Eagerly join or select author information (`username`, `avatar_url`) to avoid N+1 query overhead.
- No database migration required (uses `post_comments` table created in US3.3.1).
- Write automated Pytest suite in `backend/tests/test_US3_3_3_comments.py`.
- Full backend and frontend test suites must remain 100% passing.

## Acceptance Criteria
1. **AC1 (Auth Guard):** `POST /api/v1/posts/{id}/comments` and `DELETE /api/v1/comments/{id}` without a valid Bearer token return HTTP 401 Unauthorized with `WWW-Authenticate`.
2. **AC2 (Post Existence on Creation & Listing):** Attempting to list or create comments for a non-existent post ID returns HTTP 404 Not Found (`detail="Post not found"`).
3. **AC3 (Comment Creation Success):** An authenticated user posting valid content (1–1000 characters) creates a comment, persists it in `post_comments`, and returns HTTP 201 with `CommentOut` containing the author's username and avatar URL.
4. **AC4 (Content Validation):** Posting an empty string, whitespace-only string, or string exceeding 1000 characters returns HTTP 422 Unprocessable Entity.
5. **AC5 (Chronological Listing & Pagination):** `GET /api/v1/posts/{id}/comments` returns all comments ordered chronologically (`created_at` ascending) and supports `limit` and `offset` parameters.
6. **AC6 (Comment Author Deletion):** An authenticated user who authored a comment can delete it via `DELETE /api/v1/comments/{id}`, returning HTTP 204 No Content, removing it from subsequent listings and the database.
7. **AC7 (Admin Deletion):** An admin user (`role="admin"`) can delete any user's comment, returning HTTP 204 No Content.
8. **AC8 (Forbidden Deletion):** A non-admin user attempting to delete another user's comment receives HTTP 403 Forbidden (`detail="Not authorized to delete this comment"`).
9. **AC9 (Delete Non-existent Comment):** Attempting to delete a comment ID that does not exist returns HTTP 404 Not Found (`detail="Comment not found"`).
10. **AC10 (Automated Test Pass):** All Pytest tests in `backend/tests/test_US3_3_3_comments.py` pass cleanly with test names prefixed with `test_US3_3_3_...`.
