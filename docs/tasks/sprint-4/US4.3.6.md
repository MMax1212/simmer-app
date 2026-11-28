---
id: US4.3.6
story: US4.3
sprint: 4
assignee: Ulises Diaz
---

# Discovery integration verification

Tracks issue #71 in PR #101, using the existing Ulises branch. No production logic,
frontend code, schema, dependencies or shared test fixtures are changed.

## Coverage audit

| Requirement | Existing coverage | Added integration coverage |
| --- | --- | --- |
| Formula weights and aggregation | 4.3.1 query tests; 4.3.2 API summaries | HTTP likes on multiple posts, comments and cooking logs produce exact public scores; unlike changes the persisted score |
| Recipe-age decay | Service test with a later clock | Both API routes return independently calculated scores and reverse ordering after 24 hours; limit=1 returns the newly highest-ranked recipe |
| Preference matching | Normalization, tags, meal type, authorization, pagination and fallback tests | Real saved-profile PUTs change recommendations; a second account retains its own matches; query parameters cannot override the saved profile |
| Browser integration | Real-API matching/logout and cold-start onboarding; mobile carousel | Reused existing journeys; no duplicate browser test added |

## Why these tests

The new suite crosses HTTP write routes, persisted database rows, ranking/matching SQL,
and response serialization without mocking scoring or matching. API score/order checks
cover wiring mistakes that isolated query tests cannot detect. Multiple posts/comments
make count multiplication observable. Two real cooks respect the cooking-log cooldown.

Expected scores are literal calculations from the specification, not production constants.
A single captured clock a day ahead of writes keeps event inclusion stable; recipes have
known relative ages. Only discovery time is injected. The in-memory database fixture keeps
these tests away from local application data. Comments explain unusual setup and risks.

## Test-first and sensitivity checks

Existing ranking/matching behavior already existed, so no production bug was manufactured
to make new coverage turn green. A test setup initially attempted two logs from one cook;
the real cooldown correctly rejected the second, and the setup was corrected to two cooks.
All five new integration cases then passed without changing production code.

Three isolated child-process mutations confirmed that assertions catch:

- An incorrect like weight (3 instead of 2).
- An incorrect gravity exponent (1 instead of 1.5).
- A route ignoring saved preferences and returning fallback results.

Each mutation failed by assertion; collection/setup errors were not counted as detections.
Mutations changed in-memory globals only inside child interpreters, never repository source.

## Validation and submission boundary

- Five new integration cases passed before sensitivity checks.
- All three deliberate mistakes were caught by the relevant new cases.
- New Python file passes 100-character line length, no tabs/trailing whitespace checks.
- Full backend regression: 281 passed, with two existing dependency/duplicate-follow warnings.

Submitted with 4.3.5 in PR #101 from Ulises. Peer review and merge remain pending.
This submission does not update main. SQLite runtime is verified; PostgreSQL staging execution
remains a separate check and is not established by these tests.
