import pytest
from unittest.mock import patch
from server.models.user_model import User

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_users_state():
    return [
        User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash="dummyhash",
            is_admin=True,
        ),
        User(
            id=2,
            username="user",
            email="user@example.com",
            password_hash="dummyhash",
            is_admin=False,
        ),
    ]


def test_list_users(client, fake_users_state):
    with patch(
        "server.services.user_service.UserService.list_users",
        return_value=fake_users_state,
    ):
        res = client.get("/api/admin/users", headers=ADMIN_HEADERS)
        print("\ntest_list_users:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["username"] == "admin"
        assert data[0]["is_admin"] is True
        assert data[1]["username"] == "user"
        assert data[1]["is_admin"] is False
