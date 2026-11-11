---
id: US3.1.1
story: US3.1
sprint: 3
assignee: John Weaver
estimate_hours: 4
---

# Design and Implement Database Relational Model and Schema for Community Dish Posts

## Description
Serves **US3.1** (*Publish Food Posts on Social Feed*). Simmer is transitioning into an interactive culinary community, but the persistence layer currently only models user accounts and recipe entities. To enable users to share food creations, photo reviews, video tutorials, and mukbangs, the platform requires a dedicated `posts` relational model.

This task designs and implements the foundational `Post` database model and table schema. It establishes foreign key relationships to authors (`users.id` with cascade deletion) and optional recipe links (`recipes.id` with `SET NULL` deletion rules), caption text, required media locations (`image_url` supporting photos or videos), a `media_type` classifier (`"image"` | `"video"`), and chronological UTC timestamps with indexes.

Post authoring REST endpoints (Task 3.1.2) and post authoring modal UI (Task 3.1.3) are strictly out of scope.

## Specs
- **Model Definition (`Post` in `backend/app/models/post.py` mapped to table `posts`):**
  - `id`: Integer primary key (`autoincrement=True`).
  - `author_id`: Integer foreign key referencing `users.id` with `ondelete="CASCADE"`, indexed for rapid feed generation by author.
  - `caption`: Non-nullable Text content representing the author's description or review commentary.
  - `image_url`: Non-nullable Text string storing media locations (supporting food photos, video review links, local storage paths, or data URLs). Every post requires media.
  - `media_type`: String(20) classifying the content format (`"image"` or `"video"`, default: `"image"`).
  - `recipe_id`: Nullable Integer foreign key referencing `recipes.id` with `ondelete="SET NULL"`, indexed for recipe-associated post lookups.
  - `created_at`: DateTime with timezone (defaulting to current UTC time), indexed for chronological and algorithmic feed queries.
  - `updated_at`: DateTime with timezone (defaulting to current UTC time and updating on record modification).

- **ORM Relationships (`backend/app/models/`):**
  - `Post.author`: Many-to-one relationship to `User`, referencing `User.posts`.
  - `User.posts`: One-to-many relationship to `Post` with `cascade="all, delete-orphan"`.
  - `Post.recipe`: Optional many-to-one relationship to `Recipe`, referencing `Recipe.posts`.
  - `Recipe.posts`: One-to-many relationship to `Post` (deleting a recipe preserves the post and sets `recipe_id` to null).

- **Database Constraints & Behavior:**
  - Creating a post without a valid existing `author_id` violates foreign key constraints.
  - Attempting to persist a post without media (`image_url=None`) violates non-null database constraints.
  - Deleting an author cascades and deletes all posts published by that user.
  - Deleting a linked recipe preserves the post while nullifying `post.recipe_id`.

## Requirements
- Use SQLAlchemy 2.0 ORM Mapped columns (`Mapped`, `mapped_column`, `relationship`).
- Maintain existing user, recipe, ingredient, and audit models without data destruction.
- Export `Post` model cleanly in `backend/app/models/__init__.py`.
- Ensure all foreign keys enforce relational integrity on SQLite and PostgreSQL.
- Write unit and relational integrity tests in `backend/tests/test_US3_1_1.py`.
- Existing backend test suite must remain 100% passing.

## Acceptance criteria
1. The `posts` table schema creates successfully with all defined columns (`id`, `author_id`, `caption`, `image_url`, `media_type`, `recipe_id`, `created_at`, `updated_at`) and indexes.
2. A post can be created and persisted in the database with a linked author, caption, required media URL, media type (`"image"` or `"video"`), and optional linked recipe.
3. Persisting a post without media (`image_url=None`) fails with a database non-null integrity error.
4. Deleting a user cascades and removes all posts authored by that user.
5. Deleting a recipe that is linked to a post preserves the post entity and updates its `recipe_id` foreign key to `None`.
