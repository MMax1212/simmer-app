---
id: US3.5.2
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 3
---

# Implement Backend Follow/Unfollow Endpoints and Count Queries

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Simmer users want to follow and unfollow other creators seamlessly and inspect follower and following metrics on user profiles. 

This task implements the REST endpoints to toggle follow/unfollow status (`POST /api/v1/users/{id}/follow`) and inspect follow status and follower counts (`GET /api/v1/users/{id}/follow`). It enforces self-follow prevention, non-existent user handling, authentication guards, and optimized counting queries.

## Specs
- **Endpoints:**
  - `POST /api/v1/users/{id}/follow`:
    - Headers: `Authorization: Bearer <token>` (Required)
    - Path Param: `id` (Target user integer ID)
    - Action: Toggles follow relationship between `current_user` and target user.
    - Status Codes:
      - `HTTP 200 OK`: Successfully toggled follow state.
      - `HTTP 400 Bad Request`: If user attempts to follow themselves (`detail="You cannot follow yourself"`).
      - `HTTP 401 Unauthorized`: If request is unauthenticated.
      - `HTTP 404 Not Found`: If target user does not exist or is inactive.
    - Response Body (`FollowToggleResponse`):
      - `following` (`bool`): True if user is now following target; False if unfollowed.
      - `followers_count` (`int`): Total count of followers for target user.
      - `following_count` (`int`): Total count of users target user is following.

  - `GET /api/v1/users/{id}/follow`:
    - Headers: `Authorization: Bearer <token>` (Optional)
    - Path Param: `id` (Target user integer ID)
    - Status Codes:
      - `HTTP 200 OK`: Returns current follow metrics and whether the authenticated caller follows the target user.
      - `HTTP 404 Not Found`: If target user does not exist or is inactive.
    - Response Body (`FollowToggleResponse`):
      - `following` (`bool`): True if authenticated caller follows target; False if not (or unauthenticated).
      - `followers_count` (`int`): Total count of followers for target user.
      - `following_count` (`int`): Total count of users target user is following.

## Acceptance Criteria
1. `POST /api/v1/users/{id}/follow` when not currently following creates a `user_follows` entry and returns `following=True` and updated `followers_count`.
2. Calling `POST /api/v1/users/{id}/follow` a second time removes the relationship and returns `following=False` and decremented `followers_count`.
3. Calling follow on oneself returns HTTP 400 with `"You cannot follow yourself"`.
4. Calling follow on a non-existent user returns HTTP 404.
5. Calling follow without auth header returns HTTP 401.
6. `GET /api/v1/users/{id}/follow` accurately reports follower/following counts and whether the viewing user follows the target.
7. All 9 automated tests in `backend/tests/test_follows.py` pass cleanly.
