---
id: US4.4.1
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 4
---

# Design Database Schema Extension and Seed Data for Curated Dietary and Occasion Tags

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). To enable home cooks and community users to quickly discover and filter recipes by strict dietary requirements (e.g., vegan, vegetarian, gluten-free, keto, low-carb, dairy-free, nut-free) and popular cooking occasions (e.g., quick-dinner, under-30-mins, date-night, meal-prep, comfort-food, kid-friendly), Simmer requires standardized, curated tags in the database.

Currently, Simmer features a dynamic hashtag mechanism (`tags` table and `recipe_tags` association table) created in Sprint 2, but lacks system-seeded curated tags for standard dietary regimens and occasions.

This task extends the system tag registry with predefined dietary and occasion tags and provides an Alembic migration (`0010_dietary_and_occasion_tag_seeds.py`) that idempotently seeds these standard tags into the `tags` table without creating duplicates or breaking existing user-created tags.

Backend REST API search query extensions (Task 4.4.2), frontend filter drawer UI (Task 4.4.3), recipe card badges (Task 4.4.4), and home explore presets (Task 4.4.5) are strictly out of scope.

## Specs
- **Curated Dietary Tags:**
  - `#vegan`: Plant-based, strictly no animal products.
  - `#vegetarian`: Plant-based, excludes meat/fish, may contain dairy/eggs.
  - `#gluten-free`: Excludes wheat, barley, rye, and other gluten-containing grains.
  - `#keto`: High-fat, ketogenic, low-carb regimen.
  - `#low-carb`: Reduced carbohydrate formulation.
  - `#dairy-free`: Excludes lactose and dairy ingredients.
  - `#nut-free`: Excludes peanuts and tree nuts.

- **Curated Occasion Tags:**
  - `#quick-dinner`: Fast weeknight dinner preparation.
  - `#under-30-mins`: Meals prepared and cooked within 30 minutes.
  - `#date-night`: Romantic or elevated culinary experience.
  - `#meal-prep`: Batched recipes designed for ahead-of-time preparation.
  - `#comfort-food`: Hearty, traditional home cooking.
  - `#kid-friendly`: Mild, approachable meals suitable for children.

- **Tag Format & Normalization:**
  - Lowercase strings prefixed with `#` (e.g., `#vegan`, `#date-night`).
  - Stored in the existing `tags` table (`name` column: `String(50)`, unique, indexed).

- **Seed Migration (`backend/migrations/versions/0010_dietary_and_occasion_tag_seeds.py`):**
  - Idempotent `upgrade()`: Check for existing tag names; only insert tags that do not already exist.
  - Reversible `downgrade()`: Removes the seeded tags while preserving any user-created tags.

- **Model Relationships (`backend/app/models/recipe.py`):**
  - Verify that `Recipe.tags` and `Tag.recipes` many-to-many relationship via `recipe_tags` allows linking any recipe to these curated tags without schema changes or constraint failures.

## Requirements
- Utilize existing SQLAlchemy 2.0 ORM models (`Tag`, `recipe_tags`, `Recipe`) in `backend/app/models/recipe.py`.
- Maintain existing tables, models, and migrations without data loss or breaking schema changes.
- The seed migration must be idempotent (safe to run on databases that already contain some or all of the tags).
- Write automated tests in `backend/tests/test_US4_4_1.py` covering all acceptance criteria, with all test function names starting with `test_US4_4_1_...`.
- Maintain 100% pass rate across existing backend and frontend test suites.

## Acceptance criteria
1. The `tags` table contains all 7 curated dietary tags: `#vegan`, `#vegetarian`, `#gluten-free`, `#keto`, `#low-carb`, `#dairy-free`, and `#nut-free`.
2. The `tags` table contains all 6 curated occasion tags: `#quick-dinner`, `#under-30-mins`, `#date-night`, `#meal-prep`, `#comfort-food`, and `#kid-friendly`.
3. All seeded tag names are stored in lowercase format with a leading `#` prefix.
4. The migration is idempotent: running the migration or seed logic on a database where any of these tags already exist succeeds without `IntegrityError` or duplicate entries.
5. A recipe can be associated with multiple curated dietary tags and occasion tags via the `recipe_tags` relationship, and can be retrieved via ORM query.
6. The Alembic migration `0010_dietary_and_occasion_tag_seeds.py` executes clean `upgrade()` and `downgrade()` operations.
7. All tests in `backend/tests/test_US4_4_1.py` pass cleanly with test names prefixed with `test_US4_4_1_...`.
