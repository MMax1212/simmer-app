---
id: US3.3.1
story: US3.3
sprint: 3
assignee: Maximo Mora
estimate_hours: 4
---

# Design and Implement Database Schema and Migrations for Post Likes and Comments

## Description
Serves **US3.3** (*Likes & Comments on Community Posts*). With the foundational `posts` model established in US3.1, Simmer requires relational models and database migrations to persist user engagement. Users need to be able to like posts (with duplicate like prevention) and comment on posts (with discussion threads).

This task designs and implements the `PostLike` and `PostComment` database models and creates an Alembic migration (`0007_post_likes_and_comments.py`). It enforces foreign keys referencing `posts.id` and `users.id` with `ondelete="CASCADE"`, a unique composite constraint `uq_user_post_like` on `(user_id, post_id)` to prevent duplicate likes, and indexes for performant query delivery.

Backend REST API endpoints (Task 3.3.2 and Task 3.3.3) and frontend UI components (Task 3.3.4 and Task 3.3.5) are strictly out of scope.

## Specs
- **Model Definition (`PostLike` in `backend/app/models/post_like.py` mapped to table `post_likes`):**
  - `id`: Integer primary key (`autoincrement=True`).
  - `user_id`: Integer foreign key referencing `users.id` with `ondelete="CASCADE"`, non-nullable.
  - `post_id`: Integer foreign key referencing `posts.id` with `ondelete="CASCADE"`, non-nullable, indexed.
  - `created_at`: DateTime with timezone (default: UTC now).
  - Constraint: `UniqueConstraint("user_id", "post_id", name="uq_user_post_like")`.

- **Model Definition (`PostComment` in `backend/app/models/post_comment.py` mapped to table `post_comments`):**
  - `id`: Integer primary key (`autoincrement=True`).
  - `user_id`: Integer foreign key referencing `users.id` with `ondelete="CASCADE"`, non-nullable.
  - `post_id`: Integer foreign key referencing `posts.id` with `ondelete="CASCADE"`, non-nullable, indexed.
  - `content`: Non-nullable Text content representing the comment body (1 to 1,000 chars).
  - `created_at`: DateTime with timezone (default: UTC now), indexed for chronological comment threads.

- **ORM Relationships (`backend/app/models/`):**
  - `Post.likes`: One-to-many relationship to `PostLike` with `cascade="all, delete-orphan"`.
  - `Post.comments`: One-to-many relationship to `PostComment` with `cascade="all, delete-orphan"`.
  - `User.post_likes`: One-to-many relationship to `PostLike` with `cascade="all, delete-orphan"`.
  - `User.post_comments`: One-to-many relationship to `PostComment` with `cascade="all, delete-orphan"`.

- **Database Cascade & Integrity Constraints:**
  - Deleting a post automatically deletes all of its likes and comments (`ON DELETE CASCADE`).
  - Deleting a user automatically deletes all likes and comments authored by that user.
  - Attempting to insert a duplicate like for the same `(user_id, post_id)` violates `uq_user_post_like`.
  - Attempting to insert a comment without content violates non-null constraint.

## Requirements
- Use SQLAlchemy 2.0 ORM Mapped columns (`Mapped`, `mapped_column`, `relationship`).
- Maintain existing tables, models, and migrations without data loss.
- Export `PostLike` and `PostComment` in `backend/app/models/__init__.py`.
- Create Alembic revision `0007_post_likes_and_comments.py` with clean `upgrade()` and `downgrade()`.
- Write unit and schema integrity tests in `backend/tests/test_US3_3_1.py`.
- All existing tests in backend and frontend must remain 100% passing.

## Acceptance criteria
1. The `post_likes` table schema creates with `id`, `user_id`, `post_id`, `created_at`, indexes, and unique composite constraint `uq_user_post_like`.
2. The `post_comments` table schema creates with `id`, `user_id`, `post_id`, `content`, `created_at`, and indexes.
3. A user can like a post, and attempting to like the same post twice by the same user raises a database `IntegrityError`.
4. A user can author a comment on a post, and attempting to persist a comment with null content raises a database `IntegrityError`.
5. Deleting a post cascades and automatically deletes all associated likes and comments.
6. Deleting a user cascades and automatically deletes all likes and comments authored by that user.
7. Alembic migration `0007_post_likes_and_comments.py` upgrades and downgrades cleanly without errors.
8. All Pytest tests in `backend/tests/test_US3_3_1.py` pass cleanly with test names prefixed with `test_US3_3_1_...`.
