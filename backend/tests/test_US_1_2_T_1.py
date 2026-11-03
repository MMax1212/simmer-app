"""Tests for US-1.2-T-1: Admin Audit Log Inspection API.

Each test is mapped directly to an acceptance criterion in docs/tasks/sprint-2/US-1.2-T-1.md.
"""
from datetime import datetime, timezone

from app.models import AdminAudit
from tests.conftest import auth_headers, register


def test_US_1_2_T_1_criterion_1_unauthenticated_request_rejected(client):
    """US-1.2-T-1: Criterion 1 - Unauthenticated request returns 401."""
    response = client.get("/api/v1/admin/audit-logs")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_US_1_2_T_1_criterion_2_non_admin_forbidden(client):
    """US-1.2-T-1: Criterion 2 - Authenticated non-admin receives 403 Forbidden."""
    user_headers = auth_headers(client, email="regular@example.com", username="regular")
    response = client.get("/api/v1/admin/audit-logs", headers=user_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admins only"


def test_US_1_2_T_1_criterion_3_admin_reads_all_newest_first(client, make_admin, db_session):
    """US-1.2-T-1: Criterion 3 - Admin receives list of audit records ordered newest first."""
    admin_headers = auth_headers(client, email="boss@example.com", username="boss")
    make_admin("boss@example.com")

    # Initially empty
    initial_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert initial_res.status_code == 200
    assert initial_res.json() == []

    # Create target users and perform admin modifications to populate audit logs
    register(client, email="user1@example.com", username="user1")
    register(client, email="user2@example.com", username="user2")

    users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    u1_id = next(u["id"] for u in users if u["username"] == "user1")
    u2_id = next(u["id"] for u in users if u["username"] == "user2")

    # Action 1: Deactivate user 1
    res1 = client.patch(f"/api/v1/admin/users/{u1_id}/status", headers=admin_headers, json={"is_active": False})
    assert res1.status_code == 200

    # Action 2: Promote user 2 to admin
    res2 = client.patch(f"/api/v1/admin/users/{u2_id}/status", headers=admin_headers, json={"role": "admin"})
    assert res2.status_code == 200

    # Fetch audit logs
    audit_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()

    assert len(logs) == 2
    # Verify newest record is first (Action 2 then Action 1)
    assert logs[0]["target_id"] == u2_id
    assert logs[0]["after"]["role"] == "admin"
    assert logs[1]["target_id"] == u1_id
    assert logs[1]["after"]["is_active"] is False


def test_US_1_2_T_1_criterion_4_filter_by_target_id(client, make_admin, db_session):
    """US-1.2-T-1: Criterion 4 - ?target_id=<id> filters records to that user only."""
    admin_headers = auth_headers(client, email="admin4@example.com", username="admin4")
    make_admin("admin4@example.com")

    register(client, email="target_a@example.com", username="target_a")
    register(client, email="target_b@example.com", username="target_b")

    users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    id_a = next(u["id"] for u in users if u["username"] == "target_a")
    id_b = next(u["id"] for u in users if u["username"] == "target_b")

    client.patch(f"/api/v1/admin/users/{id_a}/status", headers=admin_headers, json={"is_active": False})
    client.patch(f"/api/v1/admin/users/{id_b}/status", headers=admin_headers, json={"role": "admin"})
    client.patch(f"/api/v1/admin/users/{id_a}/status", headers=admin_headers, json={"is_active": True})

    # Filter for target_a only
    res_a = client.get(f"/api/v1/admin/audit-logs?target_id={id_a}", headers=admin_headers)
    assert res_a.status_code == 200
    logs_a = res_a.json()
    assert len(logs_a) == 2
    assert all(log["target_id"] == id_a for log in logs_a)

    # Filter for target_b only
    res_b = client.get(f"/api/v1/admin/audit-logs?target_id={id_b}", headers=admin_headers)
    assert res_b.status_code == 200
    logs_b = res_b.json()
    assert len(logs_b) == 1
    assert logs_b[0]["target_id"] == id_b

    # Filter for user with no audit entries returns empty list
    res_empty = client.get("/api/v1/admin/audit-logs?target_id=99999", headers=admin_headers)
    assert res_empty.status_code == 200
    assert res_empty.json() == []


def test_US_1_2_T_1_criterion_5_pagination_limit_and_offset(client, make_admin, db_session):
    """US-1.2-T-1: Criterion 5 - ?limit=N&offset=M paginates results."""
    admin_headers = auth_headers(client, email="admin5@example.com", username="admin5")
    make_admin("admin5@example.com")

    register(client, email="user_page@example.com", username="user_page")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    uid = next(u["id"] for u in users if u["username"] == "user_page")

    # Generate 5 audit entries
    for _ in range(5):
        client.patch(f"/api/v1/admin/users/{uid}/status", headers=admin_headers, json={"is_active": False})
        client.patch(f"/api/v1/admin/users/{uid}/status", headers=admin_headers, json={"is_active": True})

    all_logs = client.get("/api/v1/admin/audit-logs", headers=admin_headers).json()
    assert len(all_logs) == 10

    # Limit = 3, Offset = 0 (first 3)
    p1 = client.get("/api/v1/admin/audit-logs?limit=3&offset=0", headers=admin_headers).json()
    assert len(p1) == 3
    assert p1 == all_logs[0:3]

    # Limit = 3, Offset = 3 (next 3)
    p2 = client.get("/api/v1/admin/audit-logs?limit=3&offset=3", headers=admin_headers).json()
    assert len(p2) == 3
    assert p2 == all_logs[3:6]

    # Invalid pagination parameters return 422
    assert client.get("/api/v1/admin/audit-logs?limit=0", headers=admin_headers).status_code == 422
    assert client.get("/api/v1/admin/audit-logs?limit=101", headers=admin_headers).status_code == 422
    assert client.get("/api/v1/admin/audit-logs?offset=-1", headers=admin_headers).status_code == 422
