---
id: US-1.2-T-2
story: US-1.2
sprint: 2
assignee: John Weaver
estimate_hours: 3
---

# Admin Dashboard Metrics and Account Filtering API

## Description
Serves US-1.2 (Admin Account & RBAC). While administrators can view a flat list of users and update individual statuses, the platform currently lacks system-level dashboard metrics and account filtering capabilities. An administrator reviewing system activity or assisting users cannot view aggregate community stats (such as active vs. deactivated accounts or published recipe totals) and cannot filter accounts by role or operational status.

This task implements a dedicated system metrics summary endpoint (`GET /api/v1/admin/stats`) and adds query parameter filtering (`role` and `is_active`) to the existing user management endpoint (`GET /api/v1/admin/users`).

Frontend charting/visualization components and complex multi-column text search are strictly out of scope.

## Specs
- `GET /api/v1/admin/stats`:
  - Requires admin authorization via `AdminUser` dependency (`role == "admin"`).
  - Unauthenticated requests return HTTP 401 Unauthorized with header `WWW-Authenticate: Bearer`.
  - Non-admin authenticated requests return HTTP 403 Forbidden with `{ "detail": "Admins only" }`.
  - Returns HTTP 200 and a JSON object conforming to `AdminStatsResponse`:
    - `total_users` (`int`): Total count of registered users in the database.
    - `active_users` (`int`): Count of users where `is_active == true`.
    - `deactivated_users` (`int`): Count of users where `is_active == false`.
    - `admin_users` (`int`): Count of users where `role == "admin"`.
    - `total_recipes` (`int`): Total count of published recipes in the system (the platform's current recipe-post content model).
  - Aggregate values are computed efficiently using SQL count expressions (`func.count()`).
- `GET /api/v1/admin/users`:
  - Continues to require admin authorization (`AdminUser`).
  - Supports optional query parameters for account review:
    - `role` (optional `str`): Filter users by role (`"user"` or `"admin"`).
    - `is_active` (optional `bool`): Filter users by status (`true` or `false`).
  - When query parameters are omitted, returns all users ordered by `User.id` as before (backward compatibility).
  - When filters are provided, returns only users matching all applied filters.
  - Returns HTTP 200 with an empty list `[]` when no users match the filter criteria.

## Requirements
- Use existing `User` model from `app.models.user` and `Recipe` model from `app.models.recipe`.
- Use existing `AdminUser` and `DbSession` dependencies from `app.api.deps`.
- Define `AdminStatsResponse` schema in `app.schemas.admin` (or `app.schemas.user`).
- Mount `GET /api/v1/admin/stats` and update `GET /api/v1/admin/users` in `app/api/admin.py`.
- No database schema migrations required (queries utilize existing columns and indexes).
- Existing backend test suite must remain 100% passing with zero regressions.

## Acceptance criteria
1. An unauthenticated request to `GET /api/v1/admin/stats` returns HTTP 401 Unauthorized, and a non-admin authenticated request returns HTTP 403 Forbidden.
2. An authenticated admin request to `GET /api/v1/admin/stats` returns HTTP 200 with accurate integer counts for `total_users`, `active_users`, `deactivated_users`, `admin_users`, and `total_recipes`.
3. An admin request to `GET /api/v1/admin/users?role=admin` returns HTTP 200 with only user accounts having `role == "admin"`.
4. An admin request to `GET /api/v1/admin/users?is_active=false` returns HTTP 200 with only user accounts having `is_active == false`.
5. An admin request to `GET /api/v1/admin/users` with filters matching no accounts (e.g. `?role=admin&is_active=false` when all admins are active) returns HTTP 200 with an empty list `[]`.
