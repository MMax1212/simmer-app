---
id: US-1.2-T-1
story: US-1.2
sprint: 2
assignee: John Weaver
estimate_hours: 3
---

# Admin Audit Log Inspection API

## Description
Serves US-1.2 (Admin Account & RBAC). The Simmer application records administrative actions (role changes, account deactivation/reactivation) into an `AdminAudit` database model, but currently lacks an API endpoint for administrators to inspect this audit trail.

This task implements a secure, read-only REST API endpoint (`GET /api/v1/admin/audit-logs`) that allows authorized administrators to retrieve and filter historical audit events. It includes support for target user filtering, limit/offset pagination, and newest-first chronological sorting.

Frontend UI integration (US-1.2-T-5) and audit log purging/deletion are strictly out of scope.

## Specs
- `GET /api/v1/admin/audit-logs`:
  - Requires admin authorization via `AdminUser` dependency (`role == "admin"`).
  - Unauthenticated requests return HTTP 401 Unauthorized with header `WWW-Authenticate: Bearer`.
  - Non-admin authenticated requests return HTTP 403 Forbidden with `{ "detail": "Admins only" }`.
  - Query parameters:
    - `target_id` (optional `int`): Filters records by the modified user's ID (`target_id`).
    - `limit` (optional `int`, default `50`, min `1`, max `100`): Maximum number of records to return.
    - `offset` (optional `int`, default `0`, min `0`): Number of records to skip for pagination.
  - Returns HTTP 200 and a JSON list of audit objects conforming to `AdminAuditResponse`:
    - `id` (`int`)
    - `admin_id` (`int`)
    - `target_id` (`int`)
    - `before` (`dict`)
    - `after` (`dict`)
    - `created_at` (`datetime`)
  - Results are sorted descending by `created_at` and `id` (newest records first).
  - When no records match, returns HTTP 200 with an empty list `[]`.
  - Supplying invalid pagination parameters (`limit <= 0`, `limit > 100`, or `offset < 0`) returns HTTP 422 Unprocessable Entity.

## Requirements
- Use existing `AdminAudit` model from `app.models.audit`.
- Use existing `AdminUser` and `DbSession` dependencies from `app.api.deps`.
- Define `AdminAuditResponse` schema in `app.schemas.audit` (or `app.schemas.user`).
- Mount endpoint under existing `router` in `app/api/admin.py`.
- No modification to existing user, recipe, or authentication database schemas.
- Existing backend test suite must remain 100% passing.

## Acceptance criteria
1. An unauthenticated request to `GET /api/v1/admin/audit-logs` returns HTTP 401 Unauthorized.
2. An authenticated non-admin request to `GET /api/v1/admin/audit-logs` returns HTTP 403 Forbidden.
3. An authenticated admin request to `GET /api/v1/admin/audit-logs` returns HTTP 200 with a list of audit records ordered newest first.
4. An admin request with `?target_id=<id>` returns only audit records associated with that target user ID.
5. An admin request with pagination parameters `?limit=N&offset=M` returns at most `N` records skipping the first `M` records.
