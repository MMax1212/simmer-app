---
id: US4.3.1
story: US4.3
sprint: 4
assignee: Ulises Diaz
estimate_hours: 4
---

# Trending recipe ranking query

Assignment: GitHub issue #61 and the Sprint 4 Plan Section 6 story/task identifiers. The description in that table incorrectly refers to grocery aggregation. This implementation follows the confirmed US4.3.1 trending task, not grocery work.

## Current scoring contract

The original increment used an experimental per-event decay policy while no exact
formula was available. Task 4.3.2 supersedes that policy to follow the subsequently
merged `docs/spec_4.md` and `docs/intent_4.md`:

`score = (likes*2 + comments*3 + cooking_logs*5)/(recipe_age_hours+2)^1.5`

Weights, the two-hour offset and exponent are named specification constants. All
engagement through the supplied UTC clock counts; there is no lookback cutoff.

## Query behavior

- Combine likes/comments through recipe-linked posts and direct cooking completions.
- UNION ALL preserves one event per row, preventing multiplied engagement counts.
- Exclude unlinked posts, future events and future-dated recipes.
- Aggregate once per recipe; default service returns positive-score recipes only.
- Endpoint callers opt into global cold-start fallback, selected before pagination.
- Sort by score descending then ID ascending. SQL limit is 1–20 (default 10), offset >=0.
- Return typed TrendingRecipe records with score and likes/comments/completed counts.
- Validate a timezone-aware clock, normalize to UTC, and validate internal pagination.
- Execute one SELECT without committing or mutating; caller-owned autoflush still applies.
- Use eager joins for owner/tags and unique ORM rows to prevent duplicate cards/extra queries.
- Timestamp arithmetic supports SQLite and PostgreSQL expressions. SQLite runtime is tested;
  PostgreSQL execution still requires staging verification. Other dialects raise an error.

## TDD and style

The placeholder returned an empty list. Before implementation, 16 tests failed and one empty-database test passed. The implementation made the initial 17 tests pass. Additional checks cover equivalent UTC-offset clocks and a single read-only query.

New Python follows docs/Code-Standards.md: descriptive constants, double quotes, four-space indentation, 100-character lines, type annotations and explanatory comments/docstrings. No unrelated legacy formatting changes are included.

## Verification and review boundary

The initial implementation passed 19 query tests and the then-current 200 backend tests.
The Task 4.3.2 alignment updates the regression suite to independently verify gravity,
recipe-age decay, old/future engagement, aggregation, pagination, UTC clocks and one-query
reads. See US4.3.2.md and PR #99 for current validation and API contracts.

All changes remain on the existing Ulises branch. PostgreSQL staging verification and
peer review remain required before claiming production readiness.
