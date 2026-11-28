---
id: US4.2.5
story: US4.2
sprint: 4
assignee: Benjamin Ong
estimate_hours: 4
---

# Build Interactive Grocery Checklist Page with Aisle Departments and Strike-Throughs

## Description
Serves **US4.2** (*Multi-Recipe Grocery Checklist Generator*). When shopping at the grocery store, users need an intuitive, accessible checklist that organizes consolidated ingredients by supermarket aisle departments (`Produce`, `Meat & Seafood`, `Dairy & Refrigerated`, `Pantry & Baking`, `Other`), supports strike-through progress tracking, allows item removal, and supports manual quick-add for unexpected kitchen essentials.

This task implements `GroceryPage.tsx` at `/grocery`, wired to the backend REST API endpoints (`GET /api/v1/grocery-list`, `PATCH /api/v1/grocery-items/{id}`, `POST /api/v1/grocery-items`, `DELETE /api/v1/grocery-items/{id}`).

Backend aggregation algorithms (Task 4.2.1), database models (Task 4.2.2), REST API (Task 4.2.3), and the recipe selection modal (Task 4.2.4) are already complete.

## Specs
- **Page Component (`GroceryPage.tsx` at `/grocery`):**
  - Fetches the user's active grocery checklist on mount.
  - Groups items under 5 standard supermarket aisle headers: `Produce`, `Meat & Seafood`, `Dairy & Refrigerated`, `Pantry & Baking`, and `Other`.
  - Item strike-through: clicking toggles completion with optimistic state update and calls `api.updateGroceryItem(id, { is_checked })`.
  - Manual entry bar: input for name, amount, unit, and department calling `api.addGroceryItem`.
  - Delete action: trash button calling `api.deleteGroceryItem(id)`.
  - Shopping progress bar displaying `X of Y items purchased (Z%)`.
  - Empty state displaying helpful guidance and link to `/recipes`.
- **Navigation:**
  - Route `/grocery` protected by `ProtectedRoute`.
  - "Grocery" link in `Navbar.tsx` when authenticated.

## Requirements
- Conforms to React 18, TypeScript, and Tailwind CSS.
- Zero TypeScript and build errors (`npm run build`).
- Full automated test coverage in `frontend/src/test/GroceryPage.test.tsx`.
- 100% test pass rate across existing frontend suites.

## Acceptance criteria
1. `/grocery` renders the checklist title and all items grouped by supermarket aisle.
2. Clicking an item toggles its checkbox and applies line-through strike-through styling.
3. Adding a manual item via the entry bar adds the item to the list and displays it under its department.
4. Clicking delete removes the item from the list.
5. Shopping progress bar accurately reflects the percentage and count of checked items.
6. Empty checklist displays empty state guidance with an "Explore Recipes" action button.
