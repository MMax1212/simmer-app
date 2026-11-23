---
id: US4.2.1
story: US4.2
sprint: 4
assignee: Benjamin Ong
estimate_hours: 5
---

# Implement Ingredient Name Stemming and Unit Aggregation Service Using SPK-3.1 Algorithms

## Description
Serves **US4.2** (*Multi-Recipe Grocery Checklist Generator*). When planning weekly meals, home cooks frequently select multiple recipes whose ingredients overlap. Manually reading each recipe to calculate total grocery quantities is error-prone, tedious, and causes kitchen prep friction.

This task implements the core algorithmic normalization and aggregation engine in `backend/app/services/grocery.py` based on research prototyped in SPK-3.1. It provides ingredient name stemming (stripping preparation noise and singularizing plurals), dimensional unit normalization and arithmetic across compatible volume and weight units, non-destructive isolation for incompatible units, and supermarket aisle department categorization.

Database models and migrations (Task 4.2.2), REST API endpoints (Task 4.2.3), and frontend UI components (Tasks 4.2.4 & 4.2.5) are strictly out of scope.

## Specs
- **Ingredient Name Stemming (`stem_ingredient_name(name)`):**
  - Lowercases, strips punctuation, and removes standalone numbers.
  - Removes common preparation noise words (`diced`, `chopped`, `minced`, `sliced`, `fresh`, `crushed`, `peeled`, `boneless`, `skinless`, etc.).
  - Singularizes irregular (`tomatoes` $\rightarrow$ `tomato`, `berries` $\rightarrow$ `berry`) and regular plural nouns (`onions` $\rightarrow$ `onion`, `cloves` $\rightarrow$ `clove`).

- **Unit Normalization & Conversion Tables (`normalize_unit(unit_str)`):**
  - Canonical unit alias mapping (`tbsp`, `tablespoons`, `tbs` $\rightarrow$ `tbsp`).
  - Compatible Volume family: Base unit = `tsp` ($1\text{ tbsp} = 3\text{ tsp}$, $1\text{ fl oz} = 6\text{ tsp}$, $1\text{ cup} = 48\text{ tsp}$, $1\text{ pint} = 96\text{ tsp}$, $1\text{ quart} = 192\text{ tsp}$, $1\text{ gallon} = 768\text{ tsp}$).
  - Compatible Weight family: Base unit = `oz` ($1\text{ lb} = 16\text{ oz}$, $1\text{ oz} = 28.3495\text{ g}$).
  - Discrete / Count units: `clove`, `pinch`, `slice`, `piece`, `can`, `dash` isolated so they are never inappropriately summed across incompatible unit types.

- **Supermarket Department Classifier (`classify_department(ingredient_name)`):**
  - `Produce`: Vegetables, fruits, fresh herbs.
  - `Meat & Seafood`: Poultry, beef, pork, fish, shellfish.
  - `Dairy & Refrigerated`: Milk, butter, cheeses, cream, eggs, yogurt.
  - `Pantry & Baking`: Oils, flours, sugars, salts, spices, dry pasta, rice, canned beans, vinegars.
  - `Other`: Unclassified ingredients.

- **Multi-Recipe Aggregation (`aggregate_ingredients(raw_items)`):**
  - Groups items by composite key `(stemmed_name, unit_family)`.
  - Sums base amounts and converts to clean, user-friendly display units (`choose_best_display_unit`).
  - Preserves source recipe ID traceability.
  - Guarantees non-destructive safety: incompatible units (e.g., $2\text{ cups}$ sugar and $1\text{ pinch}$ sugar) remain separate distinct rows.
  - Returns items sorted by department aisle order (`Produce` first, `Other` last), then alphabetically by name.

## Requirements
- Conforms to PEP 8 and `docs/Code-Standards.md` (no magic numbers, max line length 100 characters).
- Implemented in `backend/app/services/grocery.py`.
- Comprehensive automated test suite in `backend/tests/test_grocery.py`.
- 100% test pass rate across existing backend suites with zero regressions.

## Acceptance criteria
1. `stem_ingredient_name` strips preparation terms and singularizes ingredient nouns.
2. `normalize_unit` correctly categorizes volume, weight, and discrete units with exact base conversion factors.
3. Multi-recipe aggregation successfully combines fractional amounts across compatible units (e.g. $1/2\text{ cup}$ olive oil + $1/4\text{ cup}$ olive oil = $0.75\text{ cup}$ olive oil in `Pantry & Baking`).
4. Incompatible units for the same ingredient remain distinct rows without data corruption.
5. `classify_department` accurately categorizes ingredients into grocery store aisles.
6. All unit tests in `backend/tests/test_grocery.py` pass cleanly in under 1 second.
