---
id: US4.4.6
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 4
---

# Automated Multi-Facet Query Combinations and Responsive UI Verification Suite

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). This is the final task for US4.4, providing the comprehensive automated test coverage required for Definition of Done (DoD) sign-off.

While previous tasks tested individual slices in isolation (4.4.1 schema seeds, 4.4.2 API query engine, 4.4.3 drawer modal, 4.4.4 recipe card badges, 4.4.5 home presets), Task 4.4.6 validates the entire multi-facet combinatorial matrix, strict exclusions, and state synchronizations across both backend and frontend layers.

## Specs
- **Backend Combinatorial Matrix Suite (`backend/tests/test_US4_4_6_multi_facet_combinations.py`):**
  - **Simultaneous Multi-Facet Queries:** Verifies recipes matching `q` keyword, `cuisine`, multiple `dietary` tags, `occasion`, and `max_time` simultaneously evaluate as strict boolean intersections.
  - **Multi-Dietary Intersections:** Verifies comma-separated dietary inputs (`#vegan,#gluten-free,#keto`) enforce strict AND logic (recipes missing any tag are excluded).
  - **Strict Exclusions:**
    - Verifies recipes tagged `#vegetarian` never match a `#vegan` query.
    - Verifies recipes exceeding duration or missing required dietary/occasion tags are excluded.
  - **SQL Duplicate Trap Avoidance:** Verifies that joining multiple tags does not inflate row counts or compromise `total` pagination counts.
  - **Null Safety:** Verifies recipes with `NULL` prep or cook time are coalesced to 0 and handled safely without database errors.
- **Frontend End-to-End Filter Integration Suite (`frontend/src/test/US4_4_6_combinations.test.tsx`):**
  - **Multi-Facet User Journey:** Verifies combining text search, category pills, filter drawer dietary chips, occasion badges, and max time selector in `RecipesPage.tsx`.
  - **Synchronized State Transitions:** Verifies transitions from Home explore preset card $\rightarrow$ URL query params navigation $\rightarrow$ RecipesPage filter drawer state $\rightarrow$ Reset All filters.
  - **Responsive UI States & Accessibility:** Verifies active filter badges (`Filters (3)`), drawer ARIA accessibility, and Escape key dismissal.

## Requirements
- Python PEP 8 guidelines & Google TypeScript Style Guide: 2-space indentation, strict typing.
- Zero TypeScript build errors (`npm run build`).
- 100% test pass rate across existing backend and frontend test suites.
- Vitest test names prefixed with `US4.4.6` and pytest test functions named `test_US4_4_6_*`.

## Acceptance Criteria
1. Backend test suite verifies multi-dietary AND intersections return only recipes matching every requested dietary tag.
2. Backend test suite verifies simultaneous multi-facet queries (`q`, `cuisine`, `dietary`, `occasion`, `max_time`) evaluate as strict boolean intersections.
3. Backend test suite validates strict exclusion rules (recipes violating any active constraint are excluded).
4. Backend test suite verifies `total` pagination count is mathematically accurate without duplicate row inflation from tag joins.
5. Backend test suite confirms legacy recipes with `NULL` prep/cook times are safely handled with `COALESCE`.
6. Frontend test suite verifies that combining search text, cuisine pills, dietary chips, occasion badges, and max time updates the query payload and results.
7. Frontend test suite verifies full reset lifecycle across Home explore presets and RecipesPage drawer.
8. 100% test pass rate across all new and existing backend and frontend test suites with zero build warnings.
