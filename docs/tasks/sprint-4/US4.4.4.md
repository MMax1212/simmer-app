---
id: US4.4.4
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 4
---

# Implement Dietary Badge Pills and Occasion Icons on RecipeCard and RecipeDetail

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). With backend dietary/occasion tagging (US4.4.1), multi-facet search endpoints (US4.4.2), and the filter drawer UI (US4.4.3) live, users now need immediate visual confirmation of dietary suitability and meal occasions when browsing recipes in search grids and viewing full recipe details.

Currently, recipe cards on `RecipesPage.tsx` only show title, cuisine, author, cook time, and difficulty—tags are not rendered at all. On `RecipeDetail.tsx`, all tags are rendered as generic identical chips.

This task implements:
1. Reusable dietary badge pills and occasion badge components with semantic color palettes and Lucide icons.
2. A standardized `RecipeCard.tsx` component used across recipe grids that surfaces dietary badges and occasion indicators.
3. Enhanced tag rendering in `RecipeDetail.tsx` grouping dietary lifestyles and occasion badges with clear visual hierarchy.

Home explore preset cards (**Task 4.4.5**) and full combinations testing (**Task 4.4.6**) are strictly out of scope.

## Specs
- **Badge Components (`frontend/src/components/RecipeBadges.tsx` or `frontend/src/components/DietaryBadges.tsx`):**
  - **Dietary Badges:** Recognizes `#vegan`, `#vegetarian`, `#gluten-free`, `#keto`, `#low-carb`, `#dairy-free`, and `#nut-free`. Displays with distinct, accessible styling (e.g. green tones for plant-based, amber/warm tones for gluten-free/keto, blue/cyan tones for allergen-free).
  - **Occasion Badges:** Recognizes `#quick-dinner`, `#under-30-mins`, `#date-night`, `#meal-prep`, `#comfort-food`, and `#kid-friendly`. Displays with corresponding Lucide icons:
    - `#quick-dinner` / `#under-30-mins`: `Clock` / `Timer`
    - `#date-night`: `Sparkles` / `Heart`
    - `#meal-prep`: `Calendar` / `Package`
    - `#comfort-food`: `Flame` / `Utensils`
    - `#kid-friendly`: `Smile`
  - **General Tags:** Remaining non-curated tags render as standard subtle chips.
- **Recipe Card Component (`frontend/src/components/RecipeCard.tsx`):**
  - Reusable card component replacing inline recipe card markup in `RecipesPage.tsx`.
  - Renders title, cuisine, cook time, difficulty, author, and dietary badge pills / occasion badges.
  - Gracefully omits badge containers when a recipe has no tags.
- **Recipe Detail Integration (`frontend/src/pages/RecipeDetail.tsx`):**
  - Renders the enriched dietary badges and occasion icons in the recipe header/metadata section.

## Requirements
- Google TypeScript Style Guide & React Best Practices: 2-space indentation, strict typing, no `any`.
- Zero TypeScript build errors (`npm run build`).
- 100% test pass rate across all existing frontend and backend test suites.
- Vitest unit & integration tests written in `frontend/src/test/RecipeBadges.test.tsx` with all test names prefixed with `US4.4.4`.

## Acceptance Criteria
1. Dietary tags (`#vegan`, `#vegetarian`, `#gluten-free`, `#keto`, `#low-carb`, `#dairy-free`, `#nut-free`) render as distinct dietary badge pills with readable text and dietary styling.
2. Occasion tags (`#quick-dinner`, `#under-30-mins`, `#date-night`, `#meal-prep`, `#comfort-food`, `#kid-friendly`) render with corresponding Lucide icons and occasion badge styling.
3. `RecipeCard` renders dietary badge pills and occasion badges when a recipe possesses these tags.
4. Recipe cards without dietary or occasion tags render cleanly without empty badge wrappers.
5. `RecipeDetail` renders dietary badges and occasion icons in its recipe tags/metadata section.
6. Dietary and occasion badges include accessible `aria-label` or semantic markup for assistive technology.
7. All Vitest component tests in `frontend/src/test/RecipeBadges.test.tsx` pass cleanly with test names prefixed with `US4.4.4`.
