---
id: US4.2.2
story: US4.2
sprint: 4
assignee: Benjamin Ong
estimate_hours: 4
---

# Design and Create grocery_lists and grocery_items Database Tables with Foreign Keys and Alembic Migration

## Description
Serves **US4.2** (*Multi-Recipe Grocery Checklist Generator*). To allow users to persist their generated grocery shopping checklists across browser sessions and devices, Simmer requires dedicated database entities.

This task creates the relational persistence models `GroceryList` and `GroceryItem` in `backend/app/models/grocery.py` and establishes the Alembic migration `0011_grocery_lists_and_items.py`. It guarantees relational safety: deleting a user account cascades to remove their grocery lists and items; deleting a grocery list cascades to delete its items; and deleting a recipe sets `source_recipe_id = NULL` on linked items so user shopping lists remain intact without data corruption.

Backend REST API endpoints (Task 4.2.3) and frontend checklist UI (Tasks 4.2.4 & 4.2.5) are strictly out of scope.

## Specs
- **Model Definition (`GroceryList` mapped to `grocery_lists`):**
  - `id`: Integer primary key, autoincrement.
  - `user_id`: Integer foreign key (`users.id`, `ondelete="CASCADE"`), indexed.
  - `title`: String(100), default `"My Grocery List"`.
  - `created_at` & `updated_at`: DateTime with timezone (UTC).
  - Relationships: `user` (Many-to-One), `items` (One-to-Many with `cascade="all, delete-orphan"`).

- **Model Definition (`GroceryItem` mapped to `grocery_items`):**
  - `id`: Integer primary key, autoincrement.
  - `grocery_list_id`: Integer foreign key (`grocery_lists.id`, `ondelete="CASCADE"`), indexed.
  - `name`: String(100), indexed.
  - `amount`: Float, non-null, with database check constraint `amount > 0`.
  - `unit`: String(30), non-null.
  - `department`: String(50), default `"Other"`, indexed.
  - `is_checked`: Boolean, default `False`.
  - `source_recipe_id`: Nullable Integer foreign key (`recipes.id`, `ondelete="SET NULL"`), indexed.
  - `created_at`: DateTime with timezone (UTC).

- **Alembic Migration (`0011_grocery_lists_and_items.py`):**
  - Revision chained off `0010_dietary_and_occasion_tag_seeds`.
  - Fully reversible `upgrade()` and `downgrade()`.

## Requirements
- Conforms to PEP 8 and `docs/Code-Standards.md` (no magic numbers, max line length 100 characters).
- Implemented with SQLAlchemy 2.0 ORM `Mapped` and `mapped_column`.
- Automated test suite in `backend/tests/test_US4_2_2.py` mapping to all acceptance criteria.
- 100% test pass rate across existing backend suites.

## Acceptance criteria
1. `grocery_lists` table schema persists successfully with foreign key to `users.id`.
2. `grocery_items` table schema persists successfully with foreign key to `grocery_lists.id` and nullable `recipes.id`.
3. Check constraint `amount > 0` rejects zero and negative quantities.
4. Deleting a user cascades and deletes all associated grocery lists and grocery items.
5. Deleting a source recipe sets `source_recipe_id = NULL` on linked items without destroying checklist rows.
6. Alembic migration `0011_grocery_lists_and_items.py` applies cleanly on `upgrade()` and reverts cleanly on `downgrade()`.
