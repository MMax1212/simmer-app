# US2.4: Structured ingredients and kitchen tools

This slice starts from main at 71bc13d on codex/ulises-us2.4-ingredients-tools.

- Ingredient rows use the supported units: g, kg, oz, lb, cup, tbsp, tsp, ml, l, count, pinch.
- New/updated recipes require finite positive amounts and supported units. Existing measurements remain readable, including unknown legacy units; editing those requires selecting a supported unit.
- Required tools are optional names (1–80 trimmed characters, at most 50), deduplicated without regard to case. Enter/comma adds a tool; removal and editing are supported.
- Recipe create, read, personal listing and update return tools as a string array. Omitting tools on full PUT clears tools, consistent with the existing replacement contract.
- Recipe detail offers a local ingredient checklist and expandable tool list. Checklist state resets when navigating to another recipe.
- Migration 0003_recipe_tools adds only the tools table and index, with recipe deletion cascading to tools. It can be downgraded to 0002 without changing existing accounts or recipes.

## Local setup

From backend, with the backend environment activated, run `alembic upgrade head` before starting the app. Do not reset the database. No existing ingredient rows are rewritten by this migration.

## Dependencies and scope

No dependency on search, categorization/tagging, cooking history, or the feed spike. Those stories can consume the existing ingredient records and recipe tools. Coordinate shared recipe files and Alembic heads with teammates when integrating their branches.

Automatic measurement conversion is not implemented: the approved Sprint 2 technical contract specifies standard units but provides no conversion rules (especially for volume versus mass).

## Verification

Backend coverage includes all supported units, invalid input, tool normalization, create/read/list/update/delete, database cascade behavior, upgrade/downgrade, and existing-data regressions. Frontend and browser tests cover unit selection, dynamic rows, tool entry/removal, saving and checklist interactions.
