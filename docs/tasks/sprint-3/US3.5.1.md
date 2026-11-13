---
id: US3.5.1
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 3
---

# Create user_follows Database Join Table and Relationship Model

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Simmer users want to follow other home cooks to stay inspired by their latest culinary creations. To support social graph interactions and chronological feed delivery, the database layer must establish a dedicated relational join table tracking follower and following relationships.

This task creates the `user_follows` table and the `UserFollow` SQLAlchemy model. It enforces relational constraints, database-level indexes, and strict self-follow prevention.

## Specs
- **Database Table (`user_follows`):**
  - `follower_id` (`Integer`, Primary Key, Foreign Key `users.id` with `ondelete="CASCADE"`): The user initiating the follow.
  - `following_id` (`Integer`, Primary Key, Foreign Key `users.id` with `ondelete="CASCADE"`): The user being followed.
  - `created_at` (`DateTime(timezone=True)`, default: UTC now): Timestamp of follow action.

- **Constraints & Indexes:**
  - Composite Primary Key on `(follower_id, following_id)` ensuring uniqueness without duplicate follow records.
  - Check constraint `ck_user_follows_no_self_follow` (`follower_id != following_id`) preventing users from following themselves.
  - Indexes on `follower_id` and `following_id` for $O(1)$ relational lookups and count queries.

- **ORM Relationships on `User`:**
  - `following_relations`: Back-populates `UserFollow.follower` with `cascade="all, delete-orphan"`.
  - `follower_relations`: Back-populates `UserFollow.following` with `cascade="all, delete-orphan"`.

- **Alembic Migration:**
  - `backend/migrations/versions/0007_user_follows.py`
  - `revision = "0007_user_follows"`
  - `down_revision = "0006_completed_recipes"`

## Acceptance Criteria
1. Migration `0007_user_follows` applies cleanly (`upgrade head`) and reverts cleanly (`downgrade -1`).
2. A user can follow another user, creating a persistent row in `user_follows`.
3. Attempting to follow the same user a second time violates uniqueness and raises `IntegrityError`.
4. Attempting to follow oneself violates check constraint `follower_id != following_id` and raises `IntegrityError`.
5. Deleting a user cascades and deletes all related follow rows where they are the follower or the followed user.
6. All tests in `backend/tests/test_follows.py` pass with 100% assertions satisfied.
