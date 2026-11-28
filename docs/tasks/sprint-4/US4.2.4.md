---
id: US4.2.4
story: US4.2
sprint: 4
assignee: Benjamin Ong
estimate_hours: 4
---

# Build "Add to Grocery List" Multi-Recipe Selector Modal in React

## Description
Serves **US4.2** (*Multi-Recipe Grocery Checklist Generator*). To enable home cooks to easily bundle ingredients across several recipes for their weekly shopping, Simmer provides an interactive multi-recipe selector modal.

This task creates the `AddToGroceryModal.tsx` component and integrates it into `RecipeCard.tsx` and `RecipeDetail.tsx`. The modal allows pre-selecting the active recipe, selecting or deselecting additional recipes, specifying a checklist title, displaying a live recipe count preview, and submitting to the backend generation endpoint (`POST /api/v1/grocery-list/generate`).

Backend persistence (Task 4.2.2 & 4.2.3) and the standalone checklist view (Task 4.2.5) are strictly out of scope.

## Specs
- **Modal Component (`AddToGroceryModal.tsx`):**
  - Triggered with `isOpen`, `onClose`, `initialRecipeId`, `initialRecipeTitle`.
  - Automatically pre-selects the active recipe upon opening.
  - Fetches and displays available recipes with checkboxes.
  - Live selection count header: `Select Recipes (X selected)`.
  - Generates list via `api.generateGroceryList` and redirects to `/grocery`.
  - Unauthenticated access prompts: *"Please log in or create an account to save grocery checklists"*.
- **RecipeCard Trigger:**
  - Shopping cart icon button on the top corner of recipe cards.
- **RecipeDetail Trigger:**
  - "+ Add to Grocery List" action button alongside "I Cooked This".

## Requirements
- Written in TypeScript and React with Tailwind styling.
- Zero TypeScript and build errors (`npm run build`).
- Full automated test coverage in `frontend/src/test/AddToGroceryModal.test.tsx`.
- 100% test pass rate across all existing frontend tests.

## Acceptance criteria
1. Opening the modal pre-selects the triggering recipe and displays its title.
2. Users can multi-select or uncheck recipes with live count updates.
3. Submitting calls `api.generateGroceryList` with chosen recipe IDs and title.
4. On generation success, closes modal and navigates to `/grocery`.
5. Unauthenticated users are prompted with login guidance.
6. The submit button is disabled when zero recipes are selected.
