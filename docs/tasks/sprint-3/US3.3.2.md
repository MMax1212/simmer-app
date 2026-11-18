---
id: US3.3.2
story: US3.3
sprint: 3
assignee: Maximo Mora
estimate_hours: 3
---

# Implement Backend Post Like Toggle and Count API Endpoint

## Description
Serves **US3.3** (*Likes & Comments on Community Posts*). With the `PostLike` relational model and database table established in US3.3.1, Simmer requires the backend REST API endpoint to enable users to like and unlike community posts.

This task implements the `POST /api/v1/posts/{id}/like` endpoint in `backend/app/api/posts.py` and the `LikeToggleResponse` Pydantic DTO in `backend/app/schemas/post.py`. The endpoint verifies authentication, checks post existence, toggles the like state atomically (creating a new like if unliked; removing the like if already liked), and returns the new like status and updated total like count.

Comment authoring endpoints (Task 3.3.3) and frontend heart button (Task 3.3.4) are strictly out of scope.

## Specs
- **Pydantic DTO Schema (`backend/app/schemas/post.py`):**
  - `LikeToggleResponse`:
    - `liked`: `bool`
    - `likes_count`: `int`

- **REST API Endpoint (`backend/app/api/posts.py`):**
  - **Method & Route:** `POST /api/v1/posts/{id}/like`
  - **Authentication:** Required (`CurrentUser` guard; returns HTTP 401 if unauthenticated).
  - **Path Parameter:** `id` (`int`, ID of the community post).
  - **Business Logic:**
    1. Query database for target `Post` with `id`. If not found, return HTTP 404 (`"Post not found"`).
    2. Check if a `PostLike` record already exists for `(user_id=CurrentUser.id, post_id=post.id)`.
    3. If found: delete the like record (unlike action), commit, and set `liked=False`.
    4. If not found: create and insert a new `PostLike` record, commit, and set `liked=True`.
    5. Query total count of remaining likes for `post.id`.
    6. Return HTTP 200 with `LikeToggleResponse(liked=liked, likes_count=total_count)`.

## Requirements
- Use FastAPI, SQLAlchemy 2.0 select queries, and Pydantic v2 schemas.
- Adhere strictly to the endpoint contract defined in `docs/sprint3/spec.md`.
- No changes to database schemas or migration files (uses tables from US3.3.1).
- Write automated Pytest suite in `backend/tests/test_US3_3_2_like_toggle.py`.
- Full backend and frontend test suites must remain 100% passing.

## Acceptance criteria
1. `POST /api/v1/posts/{id}/like` requires authentication and returns HTTP 401 when the request lacks a valid token.
2. Attempting to like a non-existent post ID returns HTTP 404 Not Found.
3. An authenticated user calling the endpoint on an unliked post adds a like and returns HTTP 200 with `liked=True` and `likes_count=1`.
4. Calling the endpoint a second time on the same post by the same user unlikes it and returns HTTP 200 with `liked=False` and `likes_count=0`.
5. Multiple distinct users liking the same post increments `likes_count` accurately.
6. Only the calling user's like status is toggled without affecting other users' like records.
7. All Pytest tests in `backend/tests/test_US3_3_2_like_toggle.py` pass cleanly with test names prefixed with `test_US3_3_2_...`.
