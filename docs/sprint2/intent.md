# Intent: Simmer Sprint 2 — Recipe Categorization, Structured Ingredients, Search & Cooking History

**Author:** Team Simmer (Product Owner: Maximo Mora)  
**Status:** Approved  
**Date:** 2026-10-26  
**Target Milestone / Branch:** `sprint-2-recipes-search` (CMPS 115 Sprint 2)  
**Reference Docs:** [Sprint_Plan_2.md](../Sprint_Plan_2.md), [Release_Plan_v1.1.md](../Release_Plan_v1.1.md), [Architecture_Design.md](../Architecture_Design.md)

---

## 1. Problem
Sprint 1 delivered a solid foundation: users can authenticate, manage profile details, and author basic recipes. However, recipes currently lack structured data models and discoverability. Users cannot categorize recipes by cuisine or difficulty, search for meals by title or ingredients, enter structured ingredient units and kitchen tools, or keep track of recipes they have cooked. 

Furthermore, before implementing Sprint 3's community social feed, the team must evaluate feed architectures through an exploratory spike to prevent architectural rework.

---

## 2. Proposed Outcomes & Success Metrics
1. **Recipe Categorization (US2.1 — 3 pts):** Recipes can be categorized by cuisine (Italian, Mexican, Asian, etc.), meal type (Breakfast, Lunch, Dinner, Snack), and difficulty (Easy, Medium, Hard). Users can filter recipe lists by these category tags.
2. **Multi-Criteria Recipe Search (US2.2 — 5 pts):** Users can search recipes by title, keywords, or ingredient names with instant, debounced client-side queries and response times under 100ms on local datasets.
3. **Cooking History Log (US2.3 — 3 pts):** Users can log when they cook a recipe with an "I Cooked This!" action, add optional personal notes/ratings, and view their historical cooking journey on their profile.
4. **Structured Ingredients & Kitchen Tools (US2.4 — 5 pts):** Recipe authoring enforces structured ingredient entries (amount, standardized unit, ingredient name) and allows tagging required kitchen tools (e.g., Blender, Cast Iron Skillet).
5. **Social Feed Architecture Spike (SPK-2.1 — 2 pts):** Technical benchmark and architectural recommendation comparing fan-out-on-read vs. fan-out-on-write feed pipelines for Sprint 3.
6. **Continuous Quality & Test Coverage:** All new search queries, schema migrations, and endpoints covered by automated Pytest and Vitest test suites (maintaining 100% test pass rate).

---

## 3. Non-Goals (Out of Scope for Sprint 2)
- **Do NOT implement social interactions:** No public social feed, following/followers, post likes, comments, or public photo sharing (reserved strictly for Sprint 3).
- **Do NOT implement external cloud image hosting:** Do not wire live AWS S3 or Cloudinary API keys; continue using valid image URLs or placeholder images.
- **Do NOT build AI ingredient extraction:** Do not implement LLM/AI image parsing (Product Backlog PB-01).
- **Do NOT build grocery checklist generation:** Grocery list aggregation from multiple recipes is reserved for Sprint 4 (US4.2).

---

## 4. Guiding Principles & Trade-offs
- **Structured Data Over Free-Text:** Storing ingredients with explicit numeric amounts and standardized unit strings unlocks future unit conversion and grocery list aggregation.
- **Client-Side Debouncing for Search:** The frontend search bar must debounce user keystrokes by 300ms to eliminate unnecessary API spamming.
- **Non-Destructive Schema Evolution:** Use Alembic migrations to evolve the database without wiping existing Sprint 1 user accounts or recipe data.
- **Performance Simplicity:** Local search utilizes parameterized SQL `LIKE` and text indexing; do not over-engineer with external ElasticSearch clusters for Sprint 2.

---

## 5. Affected Users & Systems
- **Users:** Home cooks, recipe creators, and community members browsing and organizing culinary content.
- **Systems & Codebases:**
  - `backend/app/models/`: `recipe.py`, `recipe_ingredients.py`, `completed_recipes.py`.
  - `backend/app/api/`: `recipes.py` (search and filtering endpoints), `users.py` (cooking history).
  - `backend/migrations/`: Alembic migration scripts for new category columns and join tables.
  - `frontend/src/pages/`: `RecipesPage.tsx` (filter bar and search grid), `CreateRecipePage.tsx` (dynamic ingredient rows & tool selectors), `ProfilePage.tsx` (Cooking History tab).
  - `frontend/src/components/recipes/`: `SearchBar.tsx`, `CategoryPills.tsx`, `IngredientRowInput.tsx`, `CookedModal.tsx`.

---

## 6. Constraints & Guardrails
- **Backward Compatibility:** All existing Sprint 1 recipes must continue to load without errors. Recipes with missing categories must default gracefully to `"other"` or `"medium"`.
- **Measurement Units:** Standardize allowed ingredient units (e.g., `g`, `kg`, `oz`, `lb`, `cup`, `tbsp`, `tsp`, `ml`, `l`, `count`, `pinch`).
- **SQL Injection Prevention:** All search queries must use SQLAlchemy ORM expressions or parameterized queries; never concatenate raw user search strings into SQL statements.
- **Mobile Responsive Layout:** Search filter pills and dynamic ingredient rows must adapt smoothly to mobile and desktop screen widths.

---

## 7. High-Level Failure Behavior
- **No Search Results Found:** Display a friendly, accessible empty state (*"No recipes found matching your search. Try adjusting your filters or clearing keywords."*) with a single-click "Clear Filters" button.
- **Invalid Ingredient Quantity:** Reject non-numeric or negative ingredient amounts with HTTP 422 Unprocessable Entity and inline form validation errors.
- **Duplicate Cooked Log Submissions:** Prevent double-clicking "I Cooked This!" from creating duplicate entries within the same 60-second window.

---

## 8. High-Level Acceptance Scenarios
- **Scenario 1 (Structured Recipe Creation):**
  - *Given* an authenticated user on the "Create Recipe" page,
  - *When* they select cuisine "Italian", meal type "Dinner", difficulty "Medium", add 3 structured ingredients (e.g., 200 g Pasta, 2 tbsp Olive Oil), select tool "Large Pot", and save,
  - *Then* the recipe is saved with relational ingredient records and renders category badges on the recipe view.
- **Scenario 2 (Multi-Criteria Keyword Search):**
  - *Given* a library of recipes,
  - *When* a user types "Garlic" in the search bar and clicks the "Italian" category pill,
  - *Then* the recipe grid immediately updates to show only Italian recipes containing garlic in the title, description, or ingredients.
- **Scenario 3 (Logging Cooking History):**
  - *Given* a user viewing a recipe detail page,
  - *When* they click "I Cooked This!", enter optional notes (*"Added extra basil, family loved it!"*), and confirm,
  - *Then* the event is recorded in the database and appears under the "Cooking History" tab on their user profile.

---

## 9. Open Questions & Technical Spikes
- **SPK-2.1 (Bryan Moreno):** Benchmark fan-out-on-read vs. fan-out-on-write feed query performance for Sprint 3. Research whether SQLite/Postgres subqueries on followers suffice for our initial 1,000-user target.
