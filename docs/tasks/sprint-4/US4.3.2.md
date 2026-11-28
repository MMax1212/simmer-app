---
id: US4.3.2
story: US4.3
sprint: 4
assignee: Ulises Diaz
estimate_hours: 4
---

# Trending and recommended recipe API endpoints

Implements issue #62 on Ulises, tracked in PR #99. Routes precede the recipe-ID route.

## Acceptance

- Public trending and authenticated recommended return `List[TrendingRecipeOut]` exactly
  as specified in `docs/spec_4.md` sections 3.1 and 4.3.
- Default limit 10, maximum 20; optional nonnegative offset. Invalid pagination returns 422.
- Shared gravity metrics use `(likes*2 + comments*3 + completed*5)/(recipe_age_hours+2)^1.5`.
  Count all non-future activity; exclude future recipes and unlinked post engagement.
- Recommendations use only the authenticated profile, normalized cuisine/meal/tag matches,
  and distinct tags. Missing/invalid/inactive sessions return 401.
- Empty/unusable preferences fall back to average cooking rating descending, then newest
  recipe and ascending ID. With no ratings, the fallback returns newest recipes. Actual
  nonmatches remain empty. This reconciles spec top-rated with intent newest/high-rated.
- Trending falls back only on global cold start, never because a later page is empty.
- Public card fields exclude private user information. No schema or frontend changes.
- Obsolete experimental environment policy is removed; code uses named spec constants.

## TDD and documentation

Updated behavior tests before production changes: 26 failed and 7 passed against the
old implementation. Tests independently calculate gravity scores and cover recipe-age
versus event-age decay, aggregation, time boundaries, authentication, profile isolation,
list DTOs, pagination, fallback ratings and newest ordering, duplicates, and query count.
Additional regressions cover future ratings and meal/tag matching. Comments explain the
SQL aggregation, clock, fallback selection, and public serialization boundaries.

README and API_README describe the current contract. The original 4.3.1 experimental
policy is superseded by these specification-alignment changes in the same service.
PostgreSQL runtime execution remains a staging check; no migration is needed.

## Local verification after alignment

- 35 focused ranking/API tests passed.
- Full backend: 270 passed (two existing dependency/duplicate-follow warnings).
- Frontend: 79 passed; TypeScript/Vite production build passed.
- Browser integration: 2 passed.
- PostgreSQL SQL compilation passed, including explicitly typed empty ratings in UNION arms.
- Changed discovery Python files pass the 100-character, no-tabs and whitespace checks.
