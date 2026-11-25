---
id: US3.4.1
story: US3.4
sprint: 3
assignee: Benjamin Ong
pr: https://github.com/MMax1212/simmer-app/pull/44
estimate_hours: 3
---

# Design and Implement Database Schema and Migration for Saved Posts

## Description
Serves **US3.4** (*Bookmark / Save Posts*: "As a user, I want to bookmark public posts into a 'Saved Posts' collection so that I can revisit inspiring ideas later.").

This task designs and implements the `SavedPost` SQLAlchemy ORM model and Alembic migration (`0008_saved_posts.py`) to persist user-to-post bookmarks. It enforces cascading deletes on both `users.id` and `posts.id`, indexes `user_id`, `post_id`, and `created_at` for chronological retrieval, and prevents duplicate bookmarks via the composite unique constraint `uq_saved_posts_user_post`.

Backend REST API endpoints (Task 3.4.2), frontend components (Tasks 3.4.3 and 3.4.4), and integration tests (Task 3.4.5) are out of scope for this task.

## Specs
- **Model Definition (`SavedPost` in `backend/app/models/saved_post.py` mapped to table `saved_posts`):**
  - `id`: Integer primary key (`Mapped[int]`).
  - `user_id`: Integer foreign key referencing `users.id` with `ondelete="CASCADE"`, indexed.
  - `post_id`: Integer foreign key referencing `posts.id` with `ondelete="CASCADE"`, indexed.
  - `created_at`: Timezone-aware `DateTime` defaulting to UTC now, indexed for chronological retrieval.
  - Constraint: `UniqueConstraint("user_id", "post_id", name="uq_saved_posts_user_post")`.
- **ORM Relationships:**
  - `User.saved_posts` in `backend/app/models/user.py` with `cascade="all, delete-orphan"`.
  - `Post.saved_by` in `backend/app/models/post.py` with `cascade="all, delete-orphan"`.
  - `SavedPost` exported in `backend/app/models/__init__.py`.
- **Alembic Migration (`backend/migrations/versions/0008_saved_posts.py`):**
  - Chained off `0007_post_likes_and_comments` with clean `upgrade()` and `downgrade()`.

## Requirements
- Use SQLAlchemy 2.0 `Mapped` / `mapped_column` / `relationship` syntax.
- Ensure deleting a `User` or `Post` cascades to remove associated `saved_posts` rows.
- Verify bidirectional Alembic migration (`alembic upgrade head` and `alembic downgrade -1`).

## Acceptance criteria
1. The `saved_posts` table creates with `id`, `user_id`, `post_id`, `created_at`, indexes, and `uq_saved_posts_user_post`.
2. `SavedPost` is registered and exported in `backend/app/models/__init__.py`.
3. Deleting a post or user cascades and deletes associated saved post entries.
4. Alembic migration `0008_saved_posts.py` upgrades and downgrades cleanly without errors.
