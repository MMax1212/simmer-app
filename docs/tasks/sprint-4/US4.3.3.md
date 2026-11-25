---
id: US4.3.3
story: US4.3
sprint: 4
assignee: Ulises Diaz
---

# Trending carousel on Home

Tracks issue #63 in PR #99 on the existing Ulises branch, following the
4.3.2 public discovery contract. No backend changes or new dependencies.

## Behavior

- Load the top five cards via the shared public API client; preserve server order.
- Place Trending Recipes This Week above the existing Home timeline.
- Show recipe details, author, cooking time, likes and cooking count; link to recipe detail.
- Native horizontal scrolling supports touch and keyboard, with Previous/Next buttons.
  No autoplay or timed motion. A focus outline identifies the scrollable list.
- Missing images show a text placeholder; failed images do not hide recipe text.
- Independent loading, empty, failure and retry states keep feed requests independent.
- Ignore stale request completions after unmount/retry. Never send saved auth to public trending.
- Cold-start ordering comes from the server. A fallback badge and personalized section
  are separate work; the current DTO does not identify fallback responses.

## Why these tests

Test comments explain each scenario's regression risk and the boundary it covers.
Component cases check ranking preservation, missing photos, pending/empty requests,
retry recovery, Home placement, scroll direction, and public-request credentials.
The browser case checks real mobile layout, scrolling and navigation that JSDOM cannot
verify. Existing feed cases protect timeline behavior when discovery loads in parallel.
Comments should explain why a case exists or why its setup is unusual, rather than
repeat assertions. Follow this convention for future tests and test groups.

## Test-first verification

The test suite was added before the component and failed because the component was
absent. Implementation made the behavior cases pass, then coverage was expanded for
scroll controls and the actual public request. Existing feed mocks were corrected to
return fresh endpoint-specific Response bodies for parallel requests.

- Full frontend: 85 tests passed.
- TypeScript/Vite production build passed.
- Browser integration: 3 tests passed, including a 390px mobile carousel test verifying
  no page overflow, horizontal movement and recipe detail navigation.

Submitted with 4.3.2 in PR #99 from Ulises. Peer review and merge remain pending; main is unchanged by this submission.
