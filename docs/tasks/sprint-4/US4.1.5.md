---
id: US4.1.5
story: US4.1
sprint: 4
assignee: Bryan Moreno
estimate_hours: 4
---

# Build "Suggested Cooks to Follow" Carousel Component Based on Mutual Follows and Popular Creators

## Description
Serves **US4.1** (*Friend Search & Network*). Home cooks want to discover active creators and friends of friends without having to guess specific usernames. A smart recommendation carousel introduces new culinary creators directly on the home page.

This task implements:
1. **Backend Recommendation Endpoint (`GET /api/v1/users/suggested?limit=10`):**
   - Ranks candidate home cooks based on:
     - **Mutual Follows / Network Graph Proximity:** Users followed by people the authenticated caller already follows (2nd-degree social network connections).
     - **Popular Creators:** Total platform follower count descending as popularity score and cold-start fallback.
   - **Exclusions:** Excludes deactivated accounts (`is_active=False`), the caller themself (`current_user.id`), and users the caller already follows.
   - Batch fetches follower and following counts to prevent $N+1$ query performance issues.
2. **Frontend API Client:**
   - Adds `api.getSuggestedCooks(limit)` to `frontend/src/services/api.ts`.
3. **Frontend Component (`frontend/src/components/SuggestedCooksCarousel.tsx`):**
   - Horizontal scrolling carousel with Previous and Next navigation controls.
   - Cards display chef avatar, username (`@username`), bio or culinary preferences, follower count, and an interactive `<FollowButton />`.
   - Embedded in `frontend/src/pages/Home.tsx` to provide immediate discovery and feed personalization.
4. **Automated Verification:**
   - Pytest tests in `backend/tests/test_suggested_cooks.py` verifying mutual follow prioritization, popularity ranking, and exclusions.
   - Vitest tests in `frontend/src/test/SuggestedCooksCarousel.test.tsx` verifying card rendering, scrolling, and inline follow toggles.

## Acceptance Criteria
1. `GET /api/v1/users/suggested` returns suggested users with `is_following=False` and accurate follower counts.
2. The caller and users the caller already follows are strictly excluded from suggestions.
3. Creators followed by the caller's followees (mutual follows) are prioritized over creators without shared connections.
4. Unauthenticated guests receive the top popular creators ordered by follower count.
5. `SuggestedCooksCarousel` renders suggested cards in a horizontal list with accessible Previous/Next buttons.
6. Clicking the `<FollowButton />` on a suggested card toggles follow state optimistically and updates the follower count.
7. Automated Pytest and Vitest test suites pass with 100% green status.
