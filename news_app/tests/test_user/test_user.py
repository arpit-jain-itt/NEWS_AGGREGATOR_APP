import pytest
from unittest.mock import patch
from server.models.user_model import User
from server.models.report_model import Report
from datetime import datetime

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_users_state():
    return [
        User(
            id=1,
            username="admin",
            email="admin@admin.com",
            password_hash="Dummy@098",
            is_admin=True,
        ),
        User(
            id=2,
            username="user",
            email="user@user.com",
            password_hash="Dummy@098",
            is_admin=False,
        ),
    ]


@pytest.fixture
def fake_reports_state():
    now = datetime.now()
    return [
        Report(
            id=1,
            user_id=1,
            article_id=10,
            reason="spam",
            created_at=now,
            status="pending",
        ),
        Report(
            id=2,
            user_id=1,
            article_id=11,
            reason="offensive",
            created_at=now,
            status="reviewed",
        ),
    ]


def test_register_user(client):
    with patch(
        "server.services.user_service.UserService.register_user", return_value=3
    ):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123",
        }
        res = client.post("/api/users/register", json=payload)
        print("\ntest_register_user:", res.get_json())
        assert res.status_code == 201
        assert "registered" in res.get_json().get("message", "")


def test_register_user_duplicate(client):
    with patch(
        "server.services.user_service.UserService.register_user", return_value=None
    ):
        payload = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "Password123",
        }
        res = client.post("/api/users/register", json=payload)
        print("\ntest_register_user_duplicate:", res.get_json())
        assert res.status_code == 400
        assert "exists" in res.get_json().get("message", "")


def test_register_user_error(client):
    with patch(
        "server.services.user_service.UserService.register_user",
        side_effect=Exception(),
    ):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123",
        }
        res = client.post("/api/users/register", json=payload)
        assert res.status_code in (500, 400)


def test_login_success(client, fake_users_state):
    user = fake_users_state[0]
    with patch(
        "server.services.user_service.UserService.authenticate_user", return_value=user
    ):
        payload = {"email": user.email, "password": "Password123"}
        res = client.post("/api/users/login", json=payload)
        print("\ntest_login_success:", res.get_json())
        assert res.status_code == 200
        assert "Login successful" in res.get_json().get("message", "")


def test_login_failure(client):
    with patch(
        "server.services.user_service.UserService.authenticate_user", return_value=None
    ):
        payload = {"email": "wrong@example.com", "password": "wrong"}
        res = client.post("/api/users/login", json=payload)
        print("\ntest_login_failure:", res.get_json())
        assert res.status_code == 401
        assert "Invalid" in res.get_json().get("message", "")


def test_login_error(client):
    with patch(
        "server.services.user_service.UserService.authenticate_user",
        side_effect=Exception(),
    ):
        payload = {"email": "user@user.com", "password": "Password123"}
        res = client.post("/api/users/login", json=payload)
        assert res.status_code in (500, 400)


def test_logout(client):
    res = client.post("/api/users/logout")
    print("\ntest_logout:", res.get_json())
    assert res.status_code == 200
    assert "Logged out" in res.get_json().get("message", "")


def test_list_users(client, fake_users_state):
    with patch(
        "server.services.user_service.UserService.list_users",
        return_value=fake_users_state,
    ):
        res = client.get("/api/users/users", headers=ADMIN_HEADERS)
        print("\ntest_list_users:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data[0]["username"] == "admin"


def test_my_reports(client, fake_reports_state):
    with patch(
        "server.services.user_service.UserService.get_user_reports",
        return_value=fake_reports_state,
    ):
        res = client.get("/api/users/my-reports", headers=ADMIN_HEADERS)
        print("\ntest_my_reports:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["reason"] == "spam"


def test_remove_my_report(client):
    with patch(
        "server.services.user_service.UserService.remove_user_report", return_value=True
    ):
        payload = {"article_id": 10}
        res = client.delete(
            "/api/users/my-reports", json=payload, headers=ADMIN_HEADERS
        )
        print("\ntest_remove_my_report:", res.get_json())
        assert res.status_code == 200
        assert "removed" in res.get_json().get("message", "")
