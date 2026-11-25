---
id: US3.4
story: US3.4
sprint: 3
assignee: Benjamin Ong
estimate_hours: 16
---

# Bookmark / Save Posts (Tasks 3.4.1 – 3.4.5)

## Description
Implements **US3.4** (*Bookmark / Save Posts*): *"As a user, I want to bookmark public posts into a 'Saved Posts' collection so that I can revisit inspiring ideas later."*

This task delivers the full end-to-end bookmarking feature across database schema and migration (`SavedPost` & `0008_saved_posts.py`), backend REST endpoints (`POST /api/v1/posts/{post_id}/bookmark` and `GET /api/v1/users/me/saved-posts`), frontend `<BookmarkButton />` component and API client, the Profile `"Saved Posts"` tab, and automated integration tests (`backend/tests/test_Bookmark.py`).

## Specs
- **Database Schema & Migration (`Task 3.4.1`):**
  - `SavedPost` model in `backend/app/models/saved_post.py` mapped to `saved_posts` with `user_id`, `post_id`, `created_at`, `ondelete="CASCADE"`, and `UniqueConstraint("user_id", "post_id", name="uq_saved_posts_user_post")`.
  - Relationships `User.saved_posts` and `Post.saved_by` with `cascade="all, delete-orphan"`, exported in `backend/app/models/__init__.py`.
  - Alembic migration `backend/migrations/versions/0008_saved_posts.py` chained off `0007_post_likes_and_comments`.
- **Backend REST Endpoints (`Task 3.4.2`):**
  - `POST /api/v1/posts/{post_id}/bookmark` in `backend/app/api/posts.py`: authenticated toggle returning `{"bookmarked": bool, "bookmark": bool}`, `404` if missing.
  - `GET /api/v1/users/me/saved-posts` in `backend/app/api/users.py`: authenticated listing ordered by `SavedPost.created_at.desc()`, defined before `/{username}`.
- **Frontend `<BookmarkButton />` & API Client (`Task 3.4.3`):**
  - `togglePostBookmark(postId)` and `getSavedPosts()` in `frontend/src/services/api.ts`.
  - `<BookmarkButton />` in `frontend/src/components/BookmarkButton.tsx` with optimistic UI updates, rollback on error, and `aria-label` / `aria-pressed` / `aria-busy`.
- **Profile Saved Posts Tab (`Task 3.4.4`):**
  - `"saved"` tab in `frontend/src/pages/Profile.tsx` displaying saved posts with `<BookmarkButton />`, loading state, and `"No saved posts yet"` empty state.
- **Integration Tests (`Task 3.4.5`):**
  - `create_test_post` helper in `backend/tests/conftest.py`.
  - `test_bookmark_toggle`, `test_User_Isolation`, and `test_deleted_post_handling` in `backend/tests/test_Bookmark.py`.

## Requirements
- Enforce authenticated access (`401`) and strict per-user isolation for saved posts.
- Maintain clean bidirectional Alembic migrations (`upgrade head` / `downgrade -1`).
- Keep all backend, frontend, and browser integration tests passing.

## Acceptance criteria
1. Users can bookmark and unbookmark posts idempotently via `POST /api/v1/posts/{post_id}/bookmark`.
2. `GET /api/v1/users/me/saved-posts` returns only the authenticated user's saved posts, newest first.
3. Deleting a post cascades and removes it from `saved_posts`.
4. `<BookmarkButton />` updates optimistically and rolls back on failure; Profile `"Saved Posts"` tab displays saved posts and empty/loading states.
5. All backend Pytest, frontend Vitest, TypeScript build, and CI checks pass.
