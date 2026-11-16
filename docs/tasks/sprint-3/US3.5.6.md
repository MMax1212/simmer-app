---
id: US3.5.6
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 4
---

# Automated Integration Tests for Follow Integrity, Counts, and Following Feed

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Ensures comprehensive test coverage across database relational constraints, API security and error boundaries, follower network fan-out queries, and frontend UI states following strict Test-Driven Development (TDD).

## Test Coverage Breakdown

### 1. Backend Follow Relationships & Constraints (`backend/tests/test_follows.py` - 9 tests)
- `test_user_can_follow_another_user`: Persists `UserFollow` record with composite primary key and timestamp.
- `test_cannot_follow_same_user_twice`: Primary key duplicate prevention under concurrent writes.
- `test_cannot_follow_self`: Check constraint `ck_user_follows_no_self_follow` prevents self-follow loops.
- `test_cascade_delete_on_user_removal`: Cascade deletion cleans up follower/following rows upon account removal.
- `test_follow_toggle_endpoint`: `POST /api/v1/users/{id}/follow` idempotently toggles state and updates numerical counts.
- `test_cannot_follow_self_endpoint`: Guard returns HTTP 400 when attempting self-follow.
- `test_follow_nonexistent_user_returns_404`: Proper HTTP 404 response on unknown creator ID.
- `test_unauthenticated_follow_rejected`: HTTP 401 when token is missing.
- `test_get_follow_status_and_counts_endpoint`: `GET /api/v1/users/{id}/follow` reports accurate public follower counts and contextual follow status for the viewer.

### 2. Backend Timeline Feed & Network Fan-Out (`backend/tests/test_feed.py` - 8 tests)
- `test_following_feed_requires_auth`: Protects following feed behind authentication (HTTP 401).
- `test_following_feed_empty_when_not_following`: Returns empty feed (`total: 0`, `items: []`) when user follows nobody.
- `test_following_feed_filters_by_followed_users`: Fan-out-on-read relational subquery strictly delivers posts by followed creators.
- `test_following_feed_chronological_order`: Strict reverse chronological ordering (`created_at DESC`, `id DESC`).
- `test_following_feed_pagination`: Verifies `limit` and `offset` pagination slice accuracy and total counts.
- `test_global_community_feed_accessible_publicly`: Verifies public accessibility without JWT tokens.
- `test_multi_user_follow_network_feed_isolation_and_unfollow`: Multi-hop follower network isolation (User A follows B & C; User B follows C; User C follows nobody) and dynamic feed updates upon unfollowing.
- `test_feed_linked_recipe_payload`: Posts with linked recipes deliver nested recipe summaries (`id`, `title`, `cook_time_mins`, `difficulty`).

### 3. Frontend Component & Integration Tests (`frontend/src/test/FollowButton.test.tsx` - 11 tests, `frontend/src/test/feed.test.tsx` - 6 tests)
- `<FollowButton />`:
  - Visual states: "Follow" vs "Following".
  - Interactive hover state: Displays "Unfollow" indicator when hovered.
  - Optimistic UI updates with instant count adjustments.
  - Error rollback and user alert on network failure.
  - Debouncing to prevent duplicate concurrent network submissions.
  - Self-follow suppression when `currentUserId === targetUserId`.
- Tabbed Home Feed:
  - Accessible tab switcher between "Following Feed" and "Global Community Feed".
  - Logged-in user default to "Following Feed".
  - Empty state with CTA to explore the global community.
  - Visitor login prompt when selecting the following feed.
  - Feed card rendering with embedded `<FollowButton />` and `<LikeButton />`.

## Acceptance Criteria
1. All 106 backend tests pass cleanly (`backend/.venv/bin/pytest backend/tests`).
2. All 53 frontend tests pass cleanly (`npm test --prefix frontend`).
3. Frontend TypeScript compilation and asset bundling succeed with 0 warnings/errors (`npm run build --prefix frontend`).
