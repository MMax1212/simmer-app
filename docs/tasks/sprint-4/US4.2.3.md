---
id: US4.2.3
story: US4.2
sprint: 4
assignee: Benjamin Ong
estimate_hours: 4
---

# Build Backend Grocery Checklist REST API Endpoints

## Description
Serves **US4.2** (*Multi-Recipe Grocery Checklist Generator*). To connect the frontend recipe selector modal and grocery checklist page to the persistence and aggregation engine, Simmer requires secure REST API endpoints.

This task implements the FastAPI endpoints in `backend/app/api/grocery.py` and Pydantic schemas in `backend/app/schemas/grocery.py`. It integrates the ingredient aggregation service (Task 4.2.1) and database models (Task 4.2.2) to support multi-recipe checklist generation, list querying, item completion toggling, custom item insertion, and item deletion.

Frontend UI components (Tasks 4.2.4 & 4.2.5) are strictly out of scope.

## Specs
- **`POST /api/v1/grocery-list/generate`:**
  - Authenticated endpoint accepting a list of recipe IDs and an optional checklist title.
  - Fetches ingredients across all valid recipes, runs `aggregate_ingredients`, and updates the user's checklist.
  - Returns HTTP 201 with `GroceryListOut`.
- **`GET /api/v1/grocery-list`:**
  - Authenticated endpoint returning the current user's checklist with items grouped by department.
  - Returns HTTP 200 with `GroceryListOut`.
- **`PATCH /api/v1/grocery-items/{id}`:**
  - Updates `is_checked`, `amount`, or `name`.
  - Enforces list ownership: returns HTTP 403 if a user attempts to modify another user's checklist items.
- **`POST /api/v1/grocery-items`:**
  - Adds a custom manual ingredient item to the user's checklist.
  - Automatically classifies the department aisle if not explicitly specified.
- **`DELETE /api/v1/grocery-items/{id}`:**
  - Deletes an item from the checklist.
  - Enforces list ownership: returns HTTP 403 for unauthorized users. Returns HTTP 204.

## Requirements
- Conforms to PEP 8 and `docs/Code-Standards.md` (no magic numbers, max line length 100 characters).
- Enforces Bearer JWT authentication on all endpoints (HTTP 401 for unauthenticated requests).
- Enforces item ownership on mutations (HTTP 403 for non-owners).
- 100% test pass rate across existing backend test suites.

## Acceptance criteria
1. `POST /api/v1/grocery-list/generate` generates an aggregated checklist from selected recipes with HTTP 201.
2. `GET /api/v1/grocery-list` retrieves the authenticated user's checklist with all items.
3. `PATCH /api/v1/grocery-items/{id}` toggles `is_checked` status and updates quantity.
4. `POST /api/v1/grocery-items` adds a manual custom item with auto-assigned department.
5. `DELETE /api/v1/grocery-items/{id}` removes an item returning HTTP 204.
6. Non-owners are forbidden (HTTP 403) from modifying or deleting items on another user's list.
