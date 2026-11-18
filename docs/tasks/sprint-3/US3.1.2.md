---
id: US3.1.2
story: US3.1
sprint: 3
assignee: John Weaver
estimate_hours: 4
---

# Build Backend REST API Endpoints for Post Creation and Retrieval

## Description
Serves **US3.1** (*Publish Food Posts on Social Feed*). With the foundational `posts` database table established in Task 3.1.1, the application requires backend REST API endpoints to allow authenticated community members to publish food posts and let users view individual post details.

This task implements the post creation endpoint (`POST /api/v1/posts`) and the single-post retrieval endpoint (`GET /api/v1/posts/{id}`). The creation endpoint enforces authentication, non-empty media URL validation, media type classification (`"image"` | `"video"`), and verification of optional linked recipe IDs. The retrieval endpoint provides public access to post data enriched with author usernames and recipe titles.

Frontend creation modal UI (Task 3.1.3), community feed listing (Task 3.1.4), and post update/delete lifecycles (US3.2) are strictly out of scope.

## Specs
- **DTO Schemas (`backend/app/schemas/post.py`):**
  - `PostCreate`:
    - `caption`: Non-empty string (`min_length=1`, `max_length=2000`).
    - `image_url`: Non-empty string (`min_length=1`, `max_length=1000`). Media is required.
    - `media_type`: Optional string (`Literal["image", "video"]`, default: `"image"`).
    - `recipe_id`: Optional integer referencing an existing recipe ID.
  - `PostResponse`:
    - `id`: Integer primary key.
    - `author_id`: Integer user ID.
    - `author_username`: String username of the post creator.
    - `caption`: String caption content.
    - `image_url`: String media location.
    - `media_type`: String media format (`"image"` or `"video"`).
    - `recipe_id`: Optional integer recipe ID.
    - `recipe_title`: Optional string title of the linked recipe.
    - `created_at`: Datetime in UTC.
    - `updated_at`: Datetime in UTC.

- **Endpoints (`backend/app/api/posts.py` mounted at `/api/v1/posts`):**
  - `POST /api/v1/posts`:
    - Requires authentication via `CurrentUser` dependency (`HTTP 401` on unauthenticated).
    - Accepts `PostCreate` JSON payload.
    - Returns HTTP 422 if `caption` or `image_url` is missing or empty.
    - If `recipe_id` is specified, queries `Recipe`; returns HTTP 404 with `{ "detail": "Linked recipe not found" }` if invalid.
    - Persists the new `Post` entity and returns HTTP 201 Created with `PostResponse`.
  - `GET /api/v1/posts/{id}`:
    - Public access (no authentication required).
    - Queries `Post` by ID joining author and recipe details.
    - Returns HTTP 200 with `PostResponse` if found.
    - Returns HTTP 404 with `{ "detail": "Post not found" }` if the post ID does not exist.

## Requirements
- Use FastAPI `APIRouter` with prefix `/api/v1/posts` and tag `posts`.
- Use existing `CurrentUser` and `DbSession` dependencies from `app.api.deps`.
- Use existing `Post`, `User`, and `Recipe` models from `app.models`.
- Register the new router in `app.main.py`.
- Write dedicated automated tests in `backend/tests/test_US3_1_2.py`.
- Maintain 100% test pass rate across existing test suites with zero regressions.

## Acceptance criteria
1. An unauthenticated request to `POST /api/v1/posts` returns HTTP 401 Unauthorized.
2. An authenticated user calling `POST /api/v1/posts` with valid caption, media URL, and optional linked recipe receives HTTP 201 Created and the persisted post object.
3. An authenticated request to `POST /api/v1/posts` with missing or empty `image_url` returns HTTP 422 Unprocessable Entity.
4. Calling `POST /api/v1/posts` with a non-existent `recipe_id` returns HTTP 404 Not Found with error detail "Linked recipe not found".
5. A public request to `GET /api/v1/posts/{id}` for an existing post returns HTTP 200 with author username and attached recipe details.
6. A request to `GET /api/v1/posts/{id}` for a non-existent post ID returns HTTP 404 Not Found with error detail "Post not found".
