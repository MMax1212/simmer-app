---
id: US4.3.4
story: US4.3
sprint: 4
assignee: Ulises Diaz
---

# Personalized recommendations on Home

Tracks issue #66 in PR #99, following spec_4.md sections 4.3 and 6. Implemented on the
existing Ulises branch; no backend changes or new dependencies.

## Behavior

- Signed-in users see Recommended for You between trending and the timeline.
- Fetch five cards from the authenticated recommended endpoint through api.ts.
- Preserve server preference relevance/fallback order and link to recipe detail.
- Reuse DiscoveryRecipeCard with trending for consistent public card fields/photos.
- Render loading, empty, error and retry states independently from Home's other requests.
- Hide the section and avoid private requests while authentication is unresolved or absent.
- Key request state to account and saved preferences: old cards disappear synchronously
  on account changes/preferences edits. Ignore late responses after unmount or retry.
- Server-side empty-preference fallback is preserved without calling fallback cards matches.
  Dedicated cold-start guidance/badges remain Task 4.3.5, not this increment.

## Why these tests

Component tests isolate UI and session boundaries from backend matching. Deferred promises
make pending states and late cross-account responses observable. Profile-edit/logout cases
protect against stale private suggestions. The API-client case verifies bearer headers that
component spies cannot exercise. Test comments explain these regression risks.

A real-browser test creates recipes and saves preferences via the real API, then verifies
that Home displays a matching recipe, excludes the unrelated recipe, and removes the private
section on logout while leaving public trending available. This checks the integrated path
that mocked component tests cannot prove.

## Test-first verification

After adding tests and an empty UI scaffold, five behavior tests failed and two passed.
The implementation made all seven cases pass. Existing trending tests protect the shared
card extraction; feed/admin mocks now include a separate recommendations response.

- Full frontend: 105 tests passed.
- TypeScript/Vite production build passed.
- Browser integration: 4 tests passed, including the real-API recommendation/logout journey.

Submitted for review in existing PR #99 from Ulises. Peer review and merge remain pending;
this submission does not update main.
