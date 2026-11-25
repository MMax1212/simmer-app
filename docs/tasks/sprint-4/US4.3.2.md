---
id: US4.3.2
story: US4.3
sprint: 4
assignee: Ulises Diaz
estimate_hours: 4
---

# Trending and recommended recipe API endpoints

Implements issue #62 using an isolated discovery router registered before the recipe-ID route.

## Acceptance

- Public GET /api/v1/recipes/trending returns bounded public recipe summaries and ranking metadata via the tested 4.3.1 service.
- Authenticated GET /api/v1/recipes/recommended uses only the current profile's preferences; missing/invalid/inactive sessions return 401.
- Both enforce limit 1-100 and offset >=0, returning 422 for invalid query parameters. Response envelopes provide items/limit/offset, not an uncomputed total.
- Recommendations normalize stored preferences and match cuisine, meal type and tags. Rank by matched fields/distinct tags, then creation time and ID. No duplicate recipes from tags.
- Empty or unusable preferences are explicit (personalized=false); no matches return empty items. Fallback UI and recommendations presentation remain later tasks.
- Named routes resolve correctly without breaking existing recipe-ID reads or search/list routes.
- Configuration, response contracts, empty states and security are documented in README.md and docs/API_README.md.

## TDD

Before implementation, 11 cases failed and the existing numeric-route regression passed. Initial pagination tests were corrected to require a query-parameter validation location, preventing the old dynamic route's 422 from producing a false pass. Implementation made the initial tests green; the expanded 17-case suite also covers frozen-clock/configured-weight pagination, session rejection, literal input and empty responses.

## Review decisions and boundaries

The implementation was developed before docs/spec_4.md and docs/intent_4.md arrived from main. This endpoint layer exposes validated TRENDING_* configuration and uses documented starting defaults (3/5/4 weights, 7 days, 24-hour half-weight age) for product review. Query logic itself still requires explicit values. PostgreSQL execution requires staging verification. No schema or frontend code changes are introduced. This increment is being submitted as a draft PR from Ulises. Issue #62 remains In Progress until the newly merged specification is reconciled.


## Specification alignment required before merge

- Replace the existing per-event ranking policy with the specified recipe-age gravity formula and weights.
- Align response shape and field names with the specified list DTO (`trending_score`, `completed_count`).
- Use the specified default limit of 10 and maximum of 20.
- Implement and test the specified recommendation fallback; reconcile the newest/high-rated wording across the spec and intent.

The current behavior and its tests describe this draft implementation; they do not establish compliance with those newer contracts.
