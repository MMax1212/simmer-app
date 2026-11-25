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

The plan provides no exact numerical ranking policy. This endpoint layer exposes validated TRENDING_* configuration and uses documented starting defaults (3/5/4 weights, 7 days, 24-hour half-weight age) for product review. Query logic itself still requires explicit values. PostgreSQL execution requires staging verification. No schema or frontend code changes are introduced. This increment stays local on Ulises until push is requested.
