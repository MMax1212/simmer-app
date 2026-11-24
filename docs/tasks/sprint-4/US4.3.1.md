---
id: US4.3.1
story: US4.3
sprint: 4
assignee: Ulises Diaz
estimate_hours: 4
---

# Trending recipe ranking query

Assignment: GitHub issue #61 and the Sprint 4 Plan Section 6 story/task identifiers. The description in that table incorrectly refers to grocery aggregation. This implementation follows the confirmed US4.3.1 trending task, not grocery work.

## Scope and proposed scoring contract

Implement a read-only SQLAlchemy service, `app.services.trending.rank_trending_recipes`. No new routes, schema changes, UI or recommendation matching are introduced; those are later US4.3 tasks.

The plan specifies likes, comments and time decay but no numerical formula. The service therefore requires explicit weights, lookback and decay arguments instead of hardcoding a production policy. Cooking completions are a configurable third signal from the plan's dependency analysis; a zero weight disables their score contribution.

Proposed formula for each event:

`contribution = event_weight / (1 + age_hours / decay_hours)`

The recipe score is the sum of in-window contributions. The event's weight is halved at age `decay_hours`. Time decay is based on activity timestamps, not recipe creation: an old recipe can trend when it gets new engagement. Example policy values used only in tests are 3 per like, 5 per comment, 4 per completion, a 7-day window and 24-hour half-weight age. Product-owner confirmation is still needed before selecting production policy in Task 4.3.2.

## Query behavior

- Combine likes/comments through their posts' recipe links, plus direct recipe completions.
- Use UNION ALL to preserve one row per event and prevent multiplied counts from joining engagement collections together.
- Exclude unlinked posts, stale events and future timestamps. The window includes the exact cutoff and current time.
- Aggregate each recipe once; return positive-score recipes only. Cold-start fallback is Task 4.3.5.
- Sort by descending score, then ascending recipe ID. Paginate inside SQL (limit 1–100, offset >= 0). Stable pages assume the same clock and unchanged data.
- Return a typed TrendingRecipe containing the ORM recipe, score and in-window event counts. Zero-weight signals are counted but contribute zero to the score.
- Require a timezone-aware clock and normalize it to UTC. Validate finite, nonnegative weights and positive decay/window values.
- The service itself issues one SELECT and does not commit or mutate records. Caller-owned SQLAlchemy autoflush behavior still applies; pending caller edits should be flushed before ranking.
- SQL timestamp arithmetic handles SQLite and PostgreSQL explicitly. Runtime behavior is tested on SQLite only; PostgreSQL must be verified against staging before claiming production support. Other dialects raise NotImplementedError.

## TDD and style

The placeholder returned an empty list. Before implementation, 16 tests failed and one empty-database test passed. The implementation made the initial 17 tests pass. Additional checks cover equivalent UTC-offset clocks and a single read-only query.

New Python follows docs/Code-Standards.md: descriptive constants, double quotes, four-space indentation, 100-character lines, type annotations and explanatory comments/docstrings. No unrelated legacy formatting changes are included.

## Definition-of-Done boundary

The query can be tested locally independently of later API/UI work. Weights and decay policy need product confirmation, PostgreSQL execution needs staging verification, and full task completion still requires review, CI and the team's branch/merge process.

## Local verification

- 19 ranking tests passed after the test-first implementation and eager-loading fix.
- Full backend suite: 200 passed; two existing dependency/duplicate-follow warnings.
- Frontend suite: 79 passed; production build passed.
- Fresh temporary SQLite database: `alembic upgrade head` passed.
- New Python files: no lines above 100 characters, indentation tabs, or trailing whitespace.

The one-query regression test first exposed the model's automatic select-in tag loading. Joining the recipe author/tags in the ranked query, plus uniquing ORM results, removed the extra query while retaining one result per recipe. No SQL/API data was changed to make tests pass.

Implemented on the existing Ulises branch and committed with a reference to issue #61. This increment does not create a new branch or update main. Product policy confirmation, staging verification, peer review and CI remain completion requirements.
