# Intent: Simmer Sprint 4 — Discovery, Smart Filtering, Grocery Checklist & Production Release

**Author:** Team Simmer (Product Owner: Maximo Mora, Scrum Master: John Weaver)  
**Status:** Approved  
**Date:** 2026-11-23  
**Target Milestone / Branch:** `sprint-4-release-prep` (CMPS 115 Sprint 4 — Simmer MVP v1.0)  
**Reference Docs:** [Sprint_Plan_4.md](../Sprint_Plan_4.md), [Release_Plan_v1.1.md](../Release_Plan_v1.1.md), [Architecture_Design.md](../Architecture_Design.md), [Code-Standards.md](../Code-Standards.md), [Definition_of_Done.md](../Definition_of_Done.md)

---

## 1. Problem Statement
Across Sprints 1, 2, and 3, Simmer established its complete social culinary foundation: secure user authentication, profile customization, structured recipe creation, faceted search, cooking history logging, dish post authoring, animated likes, threaded comments, post bookmarking, and following feeds.

However, to deliver the finalized **Simmer MVP (v1.0)** and achieve Release Goals 2, 3, 4, and 5:
1. **Social Discovery Gap:** Users cannot discover fellow chefs or connect with real-life friends via username lookup.
2. **Preparation Friction:** Users preparing meals for the week must manually copy ingredients across recipes onto scrap paper, rather than generating an automated, aggregated grocery checklist.
3. **Feed Personalization Gap:** Browsing inspiring community recipes is limited to chronological streams without trending algorithm highlights or personalized recommendations tailored to a user's culinary preferences.
4. **Dietary & Occasion Constraints:** Users with strict dietary regimens (vegan, gluten-free, keto) or specific cooking occasions (quick 30-min dinner, date night) lack intuitive multi-facet discovery controls.
5. **Deployment & Release Readiness:** The system operates in local development and requires containerized Docker builds, cloud database staging configurations, and automated release verification.

---

## 2. Proposed Outcomes & Success Metrics
1. **Production Staging Deployment (INF-4.1 — 3 pts):** Full-stack Docker containerization, staging cloud database with SSL and secret management, and automated GitHub Actions deployment verification.
2. **Friend Search & Culinary Network (US4.1 — 5 pts):** Fast, debounced username search allowing users to find fellow home cooks, view profile summaries, and toggle follow relationships directly from search results.
3. **Multi-Recipe Grocery Checklist Generator (US4.2 — 5 pts):** Aggregates ingredient quantities across multiple chosen recipes into a consolidated, department-sorted shopping list utilizing unit normalization and fractional arithmetic prototyped in SPK-3.1.
4. **Personalized Discovery & Trending Feed (US4.3 — 5 pts):** A dynamic trending recipe carousel scored by recent social engagement with time decay, paired with recommendations matching user profile preferences.
5. **Smart Dietary & Occasion Filtering (US4.4 — 5 pts | Feature Lead: Maximo Mora):** Multi-select dietary filter badges (vegan, vegetarian, gluten-free, keto, low-carb) and occasion presets ("Under 30 Mins", "Date Night", "Meal Prep") integrated into recipe search.
6. **Zero Regression & Release Verification:** 100% pass rate maintained across all 145+ backend tests and 79+ frontend tests, with clean production builds and zero unresolved lint/type errors.

---

## 3. Non-Goals (Out of Scope for Sprint 4 & MVP)
- **Do NOT build third-party grocery delivery checkout:** In-app grocery checkout (e.g. Instacart or Amazon Fresh API integration) is out of scope; the checklist is an interactive digital shopper utility.
- **Do NOT implement direct messaging (DM / 1-on-1 chat):** Private messaging remains deferred to post-MVP roadmap.
- **Do NOT build machine-learning computer vision:** Automatic ingredient detection from photos is not supported; ingredients remain structured text entities.
- **Do NOT support multi-tenant restaurant management:** Simmer remains focused on home chefs and community food enthusiasts.

---

## 4. Guiding Principles & Trade-offs
- **Fractional Arithmetic & Unit Aggregation:** Applying findings from SPK-3.1, ingredient additions normalize compatible units (e.g., combining $1/2\text{ cup}$ and $1/4\text{ cup}$ into $3/4\text{ cup}$; converting $3\text{ tsp}$ to $1\text{ tbsp}$). Incompatible units (e.g., $2\text{ cups}$ flour and $1\text{ pinch}$ flour) remain separate distinct line items rather than forcing inaccurate conversions.
- **Time-Decay Engagement Scoring:** Trending rank uses a gravity decay formula:
  $$\text{Score} = \frac{\text{Likes} \times 2 + \text{Comments} \times 3 + \text{CookLogs} \times 5}{(\text{AgeInHours} + 2)^{1.5}}$$
  This prevents older popular recipes from permanently dominating the trending carousel.
- **Debounced Prefix Querying:** User search dispatches with a 300ms debounce to minimize database load while providing responsive autocomplete.
- **Client-Side Checklist State with Database Persistence:** Users can check off grocery items offline with optimistic UI updates, while syncing list state to the backend.

---

## 5. Affected Users & Systems
- **Users:** Home cooks planning weekly groceries, users seeking friends, and food lovers exploring trending dishes tailored to their diet.
- **Backend Codebase:**
  - `backend/app/models/`: `grocery.py` (`GroceryList`, `GroceryItem`), `user.py`, `recipe.py`.
  - `backend/app/schemas/`: `grocery.py`, `discovery.py`, `user.py` (search DTOs).
  - `backend/app/api/`: `grocery.py`, `users.py` (search endpoint), `recipes.py` (trending and dietary filters).
  - `backend/app/services/`: `grocery_aggregator.py` (unit normalization and fraction math).
  - `backend/migrations/`: Alembic migrations for grocery tables and dietary tag seeds.
- **Frontend Codebase:**
  - `frontend/src/pages/`: `GroceryPage.tsx`, `FindFriendsPage.tsx`, `RecipesPage.tsx`, `Home.tsx`.
  - `frontend/src/components/`: `TrendingCarousel.tsx`, `AddToGroceryModal.tsx`, `DietaryFilterDrawer.tsx`, `UserSearchDropdown.tsx`.
  - `frontend/src/services/api.ts`: API methods for grocery, user search, and trending feeds.

---

## 6. Constraints & Guardrails
- **Self-Exclusion in Search:** Authenticated users searching for friends must never see their own account returned in friend search results.
- **Deactivated Account Privacy:** Deactivated user accounts (`is_active == False`) are strictly excluded from friend discovery queries.
- **Grocery Quantities:** Negative ingredient amounts are strictly prohibited; checklist amounts are validated as positive decimal numbers.
- **Checklist Item Deletion:** Deleting a recipe from the database sets `source_recipe_id = NULL` on existing grocery items (`ON DELETE SET NULL`) so user shopping lists are not corrupted.

---

## 7. High-Level Failure Behaviors
- **Cold-Start Trending State:** If a new installation has insufficient likes or cooking logs, the trending carousel gracefully falls back to the newest high-rated recipes with a friendly badge.
- **Unauthenticated Checklist Access:** Attempting to generate a grocery list without logging in prompts: *"Please log in or create an account to save grocery checklists"*, saving the selected recipe IDs in temporary session storage.
- **Empty Friend Search:** When no username matches, the UI displays: *"No home chefs found matching '<query>'. Invite your friends to join Simmer!"*.

---

## 8. High-Level Acceptance Scenarios
- **Scenario 1 (Multi-Recipe Grocery Aggregation — US4.2):**
  - *Given* an authenticated user with two recipes selected ("Garlic Pasta" needing $1/2\text{ cup}$ olive oil, and "Focaccia" needing $1/4\text{ cup}$ olive oil),
  - *When* they click "Generate Grocery Checklist",
  - *Then* a consolidated grocery list is created displaying a single aggregated line item: `"Olive Oil — 3/4 cup"` categorized under the `"Pantry & Oils"` department.
- **Scenario 2 (Smart Dietary & Occasion Filtering — US4.4 Lead: Maximo Mora):**
  - *Given* a user browsing the recipes exploration catalog,
  - *When* they select the "Vegan" dietary filter and "Under 30 Mins" occasion preset,
  - *Then* the search results dynamically update to display only recipes that carry the `#vegan` tag and have `cook_time_mins + prep_time_mins <= 30`.
- **Scenario 3 (Friend Search & Quick Follow — US4.1):**
  - *Given* a user searching for `"bryan"`,
  - *When* they type into the friend search bar,
  - *Then* a debounced dropdown displays matching chef profiles with avatar, username, and an interactive "Follow" button reflecting live follow status.
- **Scenario 4 (Trending Discovery Feed — US4.3):**
  - *Given* community posts and recipes with recent likes and cooking completions,
  - *When* a user lands on the Home explore page,
  - *Then* a "Trending This Week" carousel highlights the top 5 weighted recipes above the global feed.
- **Scenario 5 (Production Staging Health — INF-4.1):**
  - *Given* the containerized application deployed to staging,
  - *When* the automated health check queries `GET /api/health`,
  - *Then* the service returns HTTP 200 with status `"ok"` and all database connections verified.
