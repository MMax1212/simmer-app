---
id: US4.3.5
story: US4.3
sprint: 4
assignee: Ulises Diaz
---

# Cold-start discovery guidance

Tracks issue #68. Submitted from the reused Ulises branch after PR #99 merged.
No schema/backend changes or new dependencies. Builds on 4.3.2 fallback ordering.

## Behavior and choices

- Empty/unusable profile preferences show Community picks for returned suggestions and
  a Choose your preferences link to the profile editor. Do not call fallback cards matches.
- An empty catalog gets friendly onboarding with browsing/sharing links. Genuine preference
  nonmatches retain a distinct message plus next steps. Protected recipe creation handles
  anonymous visitors through the existing authentication flow.
- Trending returns positive-score cards in normal mode, or zero-score recipes when the
  backend selects global cold start. Only a nonempty all-zero response gets Fresh picks
  and an explanation; a short positive-score page never triggers fallback labeling.
- This inference relies on the existing API invariant, covered by backend ranking tests.
  If the API later mixes zero-score cards into active rankings or changes fallback scoring,
  replace it with explicit metadata. The current list DTO is preserved without extra requests.
- Keep errors/retry separate from successful empty states. Guidance is rendered only after
  success, never while loading or after an error. Preserve server ordering and profile reset.
- Shared DiscoveryEmptyState provides consistent next steps. Static inline guidance avoids
  interruptive dialogs or motion; existing cards, keyboard controls and feed remain intact.

## Why these tests

UI tests distinguish new users, genuine nonmatches, active short pages, cold-start cards,
empty installations and service failures. Comments explain those risks rather than repeat
assertions. Five cases failed and fifteen passed before implementing the new behavior;
all twenty discovery component/client cases passed after implementation.

The browser journey uses the real API on a fresh test database, creates an unengaged recipe
and a user with no preferences, verifies both fallback labels and follows the profile link.
It therefore checks that the UI's zero-score inference agrees with backend behavior.

## Verification

- Full frontend after updating from main: 120 tests passed; TypeScript/Vite production build passed.
- Browser integration: all 5 tests passed, including real-API cold-start onboarding.

Peer review and merge remain pending. This submission does not update main.
