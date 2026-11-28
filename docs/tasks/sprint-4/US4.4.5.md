---
id: US4.4.5
story: US4.4
sprint: 4
assignee: Maximo Mora
estimate_hours: 3
---

# Build Quick-Filter Preset Cards on Home Explore Page

## Description
Serves **US4.4** (*Smart Dietary & Occasion Filtering*). With the backend query engine (US4.4.2), filter drawer (US4.4.3), and dietary/occasion badge pills (US4.4.4) live, users landing on the Simmer home explore feed need intuitive, high-visibility entry points to discover recipes tailored to popular lifestyles and cooking occasions.

Currently, `Home.tsx` only offers single-select category pills (cuisine, meal type, generic tags), and recipe cards are rendered with legacy inline markup without dietary badges.

This task implements:
1. A reusable `QuickFilterPresets.tsx` component rendering visually engaging cards for curated dietary and occasion presets ("Under 30 Mins", "Plant-Based", "Date Night Dinner", "Meal Prep", "Comfort Food", "Low-Carb & Keto") with Lucide icons, descriptions, and active state indicators.
2. Interactive filtering on `Home.tsx`: selecting a preset card updates the Home discovery recipe grid via `api.searchRecipes({ dietary, occasion, max_time })`.
3. Upgrading recipe cards on `Home.tsx` to `<RecipeCard />` (from Task 4.4.4) so dietary badge pills and occasion icons are visible on the Home feed.
4. Deep-link query parameter synchronization on `RecipesPage.tsx` using `useSearchParams()` so presets can also link directly to `/recipes?occasion=under-30-mins` or `/recipes?dietary=vegan` with pre-filled filters.

Full multi-facet combinations regression testing (**Task 4.4.6**) is strictly out of scope.

## Specs
- **Preset Cards Component (`frontend/src/components/QuickFilterPresets.tsx`):**
  - Renders curated preset cards:
    - **Under 30 Mins**: `max_time: 30`, `Clock` icon, "Fast meals ready in half an hour"
    - **Plant-Based**: `dietary: "vegan,vegetarian"`, `Sparkles` icon, "Delicious vegetarian & vegan dishes"
    - **Date Night Dinner**: `occasion: "date-night"`, `Heart` icon, "Special meals made to impress"
    - **Meal Prep**: `occasion: "meal-prep"`, `Calendar` icon, "Cook once, eat all week"
    - **Comfort Food**: `occasion: "comfort-food"`, `Flame` icon, "Warm, hearty, and satisfying"
    - **Low-Carb & Keto**: `dietary: "keto,low-carb"`, `Utensils` icon, "High protein, low carbohydrate"
  - Supports `selectedPresetId: string | null` and `onSelectPreset(preset: PresetConfig | null): void`.
  - Accessible semantics with `role="group"` and `aria-pressed`.
- **Home Page Integration (`frontend/src/pages/Home.tsx`):**
  - Mounts `QuickFilterPresets` in the explore/discovery section.
  - Connects preset selections to `api.searchRecipes` query params.
  - Replaces inline card rendering with `<RecipeCard />`.
- **URL Parameter Synchronization (`frontend/src/pages/RecipesPage.tsx`):**
  - Reads `dietary`, `occasion`, and `max_time` from React Router's `useSearchParams()`.
  - Initializes filter state and drawer count from URL params.

## Requirements
- Google TypeScript Style Guide & React Best Practices: 2-space indentation, strict typing, no `any`.
- Zero TypeScript build errors (`npm run build`).
- 100% test pass rate across existing frontend and backend test suites.
- Vitest unit & integration tests written in `frontend/src/test/QuickFilterPresets.test.tsx` with test names prefixed with `US4.4.5`.

## Acceptance Criteria
1. `QuickFilterPresets` renders preset cards for curated presets: "Under 30 Mins", "Plant-Based", "Date Night Dinner", "Meal Prep", "Comfort Food", and "Low-Carb & Keto".
2. Clicking a preset card toggles its active state and passes the corresponding filter parameters (`dietary`, `occasion`, or `max_time`) to the selection callback.
3. Clicking an active preset card or reset button clears the selection and restores the unfiltered recipe discovery grid.
4. On `Home.tsx`, selecting a preset card triggers `api.searchRecipes` with the preset's parameters and updates the displayed recipes.
5. Recipes displayed in the Home discovery grid use `RecipeCard` and display dietary badge pills and occasion icons.
6. Navigating to `/recipes` with URL query parameters (`?dietary=...`, `?occasion=...`, `?max_time=...`) initializes the active filter drawer state on `RecipesPage.tsx`.
7. All Vitest component and integration tests in `frontend/src/test/QuickFilterPresets.test.tsx` pass cleanly with test names prefixed with `US4.4.5`.
