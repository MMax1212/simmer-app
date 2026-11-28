---
id: US4.4.3
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 4
---

# Build Dietary and Occasion Filter Drawer Component on Recipes Page

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). With the backend query endpoints live in US4.4.2, Simmer users need a responsive, user-friendly slide-out filter drawer on `RecipesPage.tsx` to discover recipes tailored to their dietary lifestyles and cooking occasions.

Currently, `RecipesPage.tsx` only offers single-select category chips and a keyword input. This task creates `DietaryFilterDrawer.tsx`, extends `frontend/src/services/api.ts` with the new filter parameters, and connects the drawer to live search with multi-select chips, time presets, and clear-all controls.

Recipe card badge pills (Task 4.4.4) and Home explore preset shortcuts (Task 4.4.5) are strictly out of scope.

## Specs
- **API Client Extension (`frontend/src/services/api.ts`):**
  - Update `SearchFilters` interface with `dietary?: string`, `occasion?: string`, and `max_time?: number`.
  - Serialize `dietary`, `occasion`, and `max_time` in `api.searchRecipes()`.
- **Drawer Component (`frontend/src/components/DietaryFilterDrawer.tsx`):**
  - Slide-out / modal panel toggleable via a "Filters" button next to the search input.
  - Multi-select dietary chips: `Vegan`, `Vegetarian`, `Gluten-Free`, `Keto`, `Low-Carb`, `Dairy-Free`, `Nut-Free`.
  - Occasion chips: `Quick Dinner`, `Under 30 Mins`, `Date Night`, `Meal Prep`, `Comfort Food`, `Kid-Friendly`.
  - Max cooking time selector: `15`, `30`, `45`, `60` minutes.
  - "Clear All Filters" button resetting all selections.
  - Live count indicator showing active filters count.
- **Page Integration (`frontend/src/pages/RecipesPage.tsx`):**
  - Connects selected drawer filters into the search state, triggering debounced search requests with `{ q, cuisine, dietary, occasion, max_time }`.

## Requirements
- Google TypeScript Style Guide & Airbnb React Guidelines: 2-space indentation, semicolons, PascalCase components.
- Zero TypeScript build errors (`npm run build`).
- 100% test pass rate across existing backend and frontend test suites.
- Write automated Vitest tests in `frontend/src/test/DietaryFilterDrawer.test.tsx` with test names prefixed with `US4.4.3`.

## Acceptance criteria
1. `SearchFilters` in `frontend/src/services/api.ts` accepts `dietary`, `occasion`, and `max_time`, correctly serializing them into URL query parameters.
2. Clicking the "Filters" button on `RecipesPage.tsx` opens the `DietaryFilterDrawer`.
3. Clicking dietary badge chips toggles their active state and supports selecting multiple dietary tags simultaneously.
4. Clicking occasion badge chips toggles their selection.
5. Selecting a maximum cooking time limits results to recipes within that duration.
6. Clicking "Clear All Filters" resets all dietary, occasion, and max-time selections.
7. Closing the drawer or changing filters triggers `api.searchRecipes` with the updated parameters.
8. All Vitest component tests in `frontend/src/test/DietaryFilterDrawer.test.tsx` pass cleanly with test names prefixed with `US4.4.3`.
