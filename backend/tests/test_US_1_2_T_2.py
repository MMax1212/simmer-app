"""Tests for US-1.2-T-2: Admin Dashboard Metrics and Account Filtering API.

Each test is mapped directly to an acceptance criterion in docs/tasks/sprint-2/US-1.2-T-2.md.
"""
from app.models import Recipe
from tests.conftest import auth_headers, register


def test_US_1_2_T_2_criterion_1_stats_security_guards(client):
    """US-1.2-T-2: Criterion 1 - Unauthenticated gets 401, non-admin gets 403."""
    # Unauthenticated request
    unauth_res = client.get("/api/v1/admin/stats")
    assert unauth_res.status_code == 401
    assert "WWW-Authenticate" in unauth_res.headers

    # Authenticated non-admin request
    user_headers = auth_headers(client, email="regular_stats@example.com", username="regular_stats")
    forbidden_res = client.get("/api/v1/admin/stats", headers=user_headers)
    assert forbidden_res.status_code == 403
    assert forbidden_res.json()["detail"] == "Admins only"


def test_US_1_2_T_2_criterion_2_stats_accurate_aggregate_counts(client, make_admin, db_session):
    """US-1.2-T-2: Criterion 2 - Admin receives accurate counts for all stats metrics."""
    admin_headers = auth_headers(client, email="stats_boss@example.com", username="stats_boss")
    make_admin("stats_boss@example.com")

    # Register additional users
    register(client, email="active_user@example.com", username="active_user")
    register(client, email="inactive_user@example.com", username="inactive_user")
    register(client, email="second_admin@example.com", username="second_admin")
    make_admin("second_admin@example.com")

    # Deactivate one user via admin status endpoint
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    inactive_id = next(u["id"] for u in users if u["username"] == "inactive_user")
    client.patch(f"/api/v1/admin/users/{inactive_id}/status", headers=admin_headers, json={"is_active": False})

    # Create recipes attached to users directly
    author_id = next(u["id"] for u in users if u["username"] == "active_user")
    db_session.add(Recipe(title="Tacos", description="Tasty", author_id=author_id))
    db_session.add(Recipe(title="Pasta", description="Cheesy", author_id=author_id))
    db_session.commit()

    # Query stats endpoint
    res = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()

    assert stats["total_users"] == 4  # stats_boss, active_user, inactive_user, second_admin
    assert stats["active_users"] == 3
    assert stats["deactivated_users"] == 1
    assert stats["admin_users"] == 2  # stats_boss, second_admin
    assert stats["total_posts"] == 2
    assert stats["total_recipes"] == 2
    assert stats["active_users"] + stats["deactivated_users"] == stats["total_users"]


def test_US_1_2_T_2_criterion_3_filter_users_by_role(client, make_admin):
    """US-1.2-T-2: Criterion 3 - ?role=admin returns only users with role == 'admin'."""
    admin_headers = auth_headers(client, email="filter_boss@example.com", username="filter_boss")
    make_admin("filter_boss@example.com")

    register(client, email="member1@example.com", username="member1")
    register(client, email="member2@example.com", username="member2")
    register(client, email="filter_boss2@example.com", username="filter_boss2")
    make_admin("filter_boss2@example.com")

    # Filter by role=admin
    admin_res = client.get("/api/v1/admin/users?role=admin", headers=admin_headers)
    assert admin_res.status_code == 200
    admin_list = admin_res.json()
    assert len(admin_list) == 2
    assert all(u["role"] == "admin" for u in admin_list)

    # Filter by role=user
    user_res = client.get("/api/v1/admin/users?role=user", headers=admin_headers)
    assert user_res.status_code == 200
    user_list = user_res.json()
    assert len(user_list) == 2
    assert all(u["role"] == "user" for u in user_list)


def test_US_1_2_T_2_criterion_4_filter_users_by_active_status(client, make_admin):
    """US-1.2-T-2: Criterion 4 - ?is_active=false returns only deactivated users."""
    admin_headers = auth_headers(client, email="status_boss@example.com", username="status_boss")
    make_admin("status_boss@example.com")

    register(client, email="active1@example.com", username="active1")
    register(client, email="deact1@example.com", username="deact1")

    users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    deact_id = next(u["id"] for u in users if u["username"] == "deact1")
    client.patch(f"/api/v1/admin/users/{deact_id}/status", headers=admin_headers, json={"is_active": False})

    # Filter is_active=false
    deact_res = client.get("/api/v1/admin/users?is_active=false", headers=admin_headers)
    assert deact_res.status_code == 200
    deact_list = deact_res.json()
    assert len(deact_list) == 1
    assert deact_list[0]["id"] == deact_id
    assert deact_list[0]["is_active"] is False

    # Filter is_active=true
    active_res = client.get("/api/v1/admin/users?is_active=true", headers=admin_headers)
    assert active_res.status_code == 200
    active_list = active_res.json()
    assert len(active_list) == 2  # status_boss + active1
    assert all(u["is_active"] is True for u in active_list)


def test_US_1_2_T_2_criterion_5_filter_matching_none_returns_empty(client, make_admin):
    """US-1.2-T-2: Criterion 5 - Filters matching no accounts return empty list []."""
    admin_headers = auth_headers(client, email="empty_boss@example.com", username="empty_boss")
    make_admin("empty_boss@example.com")

    # In a system where all admins are active, querying deactivated admins returns []
    res = client.get("/api/v1/admin/users?role=admin&is_active=false", headers=admin_headers)
    assert res.status_code == 200
    assert res.json() == []
