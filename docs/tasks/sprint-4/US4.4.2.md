---
id: US4.4.2
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 4
---

# Update Backend Recipe Search Engine for Multi-Select Dietary, Occasion, and Max-Time Filtering

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). With the curated dietary and occasion tags seeded into the database in US4.4.1, Simmer requires backend search engine capabilities to query recipes by these tags and cooking time constraints.

Currently, `GET /api/v1/recipes` only supports a single `tag` parameter. This task extends the endpoint to accept comma-separated `dietary` tags (enforcing boolean AND intersection), an `occasion` filter, and a `max_time` parameter filtering total preparation and cooking minutes (`prep_time_mins + cook_time_mins`).

Frontend UI components (Task 4.4.3 and Task 4.4.4) are strictly out of scope.

## Specs
- **Endpoint:** `GET /api/v1/recipes`
- **New Query Parameters:**
  - `dietary` (optional, string): Comma-separated dietary tags (e.g. `vegan,gluten-free`). Normalized to lowercase `#` tags. Only recipes matching ALL specified dietary tags are returned (strict intersection).
  - `occasion` (optional, string): Occasion tag (e.g. `quick-dinner`). Matches recipes associated with that occasion tag.
  - `max_time` (optional, integer, ge=1): Maximum combined `prep_time_mins + cook_time_mins`.
- **Combination & Presets:**
  - Must seamlessly combine with existing parameters (`q`, `cuisine`, `meal_type`, `difficulty`, `ingredient`).
  - Example: `GET /api/v1/recipes?dietary=vegan&max_time=30` returns only recipes tagged `#vegan` with `prep_time_mins + cook_time_mins <= 30`.
- **Edge Cases:**
  - Empty or whitespace query parameters are safely ignored.
  - Queries matching zero recipes return HTTP 200 with `{"total": 0, "items": []}`.

## Requirements
- Maintain SQLAlchemy 2.0 query standards and PEP 8 conventions.
- Zero breaking changes to existing search parameters or response schema (`RecipeSearchResult`).
- Document the new parameters in `docs/API_README.md`.
- Write automated tests in `backend/tests/test_US4_4_2.py` prefixed with `test_US4_4_2_...`.
- 100% test pass rate across existing backend and frontend test suites.

## Acceptance criteria
1. `GET /api/v1/recipes?dietary=vegan` filters and returns only recipes tagged with `#vegan`.
2. `GET /api/v1/recipes?dietary=vegan,gluten-free` performs strict boolean AND intersection matching, returning only recipes possessing both `#vegan` and `#gluten-free`.
3. `GET /api/v1/recipes?occasion=quick-dinner` filters and returns only recipes tagged with `#quick-dinner`.
4. `GET /api/v1/recipes?max_time=30` returns only recipes whose `(prep_time_mins + cook_time_mins) <= 30`.
5. Combined multi-facet queries (e.g., `dietary=vegan&occasion=quick-dinner&max_time=30`) enforce all constraints simultaneously.
6. Queries matching zero recipes return HTTP 200 with `total: 0` and `items: []` without throwing 500 errors.
7. `docs/API_README.md` is updated with documentation for `dietary`, `occasion`, and `max_time` parameters.
8. All tests in `backend/tests/test_US4_4_2.py` pass cleanly with test names prefixed with `test_US4_4_2_...`.
