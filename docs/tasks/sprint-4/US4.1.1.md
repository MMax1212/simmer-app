---
id: US4.1.1
story: US4.1
sprint: 4
assignee: Bryan Moreno
estimate_hours: 4
---

# Implement Backend User Search Endpoint with Prefix Matching & Pagination

## Description
Serves **US4.1** (*Friend Search & Network*). Simmer home cooks want to find fellow cooks and friends by searching for usernames so they can connect, follow each other, and discover new recipes.

This task implements the backend REST endpoint `GET /api/v1/users/search` supporting:
- Case-insensitive prefix matching on usernames (`func.lower(User.username).like(f"{q.lower()}%")`).
- Offset-based pagination with `limit` and `offset` parameters and total count reporting.
- Active user filtering (`User.is_active.is_(True)`), preventing deactivated accounts from appearing in search.
- Caller self-exclusion when authenticated (home cooks do not search for themselves to follow).
- Alphabetical result ordering (`User.username.asc()`).

## API Specification
- **Endpoint:** `GET /api/v1/users/search`
- **Query Parameters:**
  - `q` (`string`, optional, default: `""`): Search query string to match username prefixes.
  - `limit` (`integer`, optional, default: `20`, min: `1`, max: `100`): Maximum results per page.
  - `offset` (`integer`, optional, default: `0`, min: `0`): Pagination offset.
- **Headers:** `Authorization: Bearer <token>` (Optional; when provided, excludes current user and annotates follow state).
- **Responses:**
  - `HTTP 200 OK`: `UserSearchResponse`
    - `total`: Total count of matching users.
    - `limit`: Active limit.
    - `offset`: Active offset.
    - `items`: List of `UserSearchResultItem` containing public user profile information and follow annotations.

## Acceptance Criteria
1. Requests matching username prefix return matching active users (e.g., `q=mario` matches `mario_bakes` and `mario_chef`).
2. Search is strictly case-insensitive (`q=MARIO` matches `mario`).
3. Deactivated users (`is_active=False`) are never returned in search results.
4. When authenticated, the search caller is excluded from their own search results.
5. Search results are returned in alphabetical order by username.
6. Pagination parameters (`limit` and `offset`) accurately slice results and return total match count.
7. Empty query (`q=""`) returns paginated list of active users for directory discovery.
8. Automated tests in `backend/tests/test_user_search.py` pass cleanly.
