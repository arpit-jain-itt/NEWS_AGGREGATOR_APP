import pytest
from unittest.mock import patch

ADMIN_HEADERS = {"X-User-ID": "1"}


def get_message(response):
    data = response.get_json()
    return (data.get("data", {}) or {}).get("message", "") or data.get("message", "")


@pytest.fixture
def fake_categories_state():
    class FakeCategory:
        def __init__(self, name):
            self.name = name

    return [FakeCategory("general"), FakeCategory("sports")]


@pytest.fixture
def fake_prefs_state():
    return {
        "keywords": '{"categories": ["general"], "keywords": ["tesla"]}',
        "notify_via_email": True,
        "enabled": True,
    }


def test_get_notification_preferences(client, fake_prefs_state):
    with patch(
        "server.repository.notification_repository.NotificationRepository.get_notification_preferences",
        return_value=fake_prefs_state,
    ):
        res = client.get("/api/notifications/preferences?user_id=1")
        print("\ntest_get_notification_preferences:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert "categories" in data
        assert "keywords" in data


def test_get_notification_preferences_not_found(client):
    with patch(
        "server.repository.notification_repository.NotificationRepository.get_notification_preferences",
        return_value=None,
    ):
        res = client.get("/api/notifications/preferences?user_id=999")
        print("\ntest_get_notification_preferences_not_found:", res.get_json())
        assert res.status_code == 404


def test_update_notification_preferences(client, fake_categories_state):
    def update_notification_preferences(
        user_id, encoded_blob, notify_via_email, enabled
    ):
        return True

    with patch(
        "server.repository.notification_repository.NotificationRepository.update_notification_preferences",
        side_effect=update_notification_preferences,
    ), patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories_state,
    ):
        payload = {
            "user_id": 1,
            "categories": "general",
            "keywords": "tesla",
            "notify_via_email": True,
            "enabled": True,
        }
        res = client.post("/api/notifications/preferences", json=payload)
        print("\ntest_update_notification_preferences:", res.get_json())
        assert res.status_code == 200
        assert "updated" in get_message(res)


def test_update_notification_preferences_invalid_category(
    client, fake_categories_state
):
    with patch(
        "server.repository.notification_repository.NotificationRepository.update_notification_preferences",
        return_value=True,
    ), patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories_state,
    ):
        payload = {
            "user_id": 1,
            "categories": "invalidcat",
            "keywords": "tesla",
            "notify_via_email": True,
            "enabled": True,
        }
        res = client.post("/api/notifications/preferences", json=payload)
        print(
            "\ntest_update_notification_preferences_invalid_category:", res.get_json()
        )
        assert res.status_code == 400
        assert "Invalid categories" in get_message(res)


def test_remove_all_notification_preferences(client, fake_categories_state):
    def update_notification_preferences(
        user_id, encoded_blob, notify_via_email, enabled
    ):
        return True

    with patch(
        "server.repository.notification_repository.NotificationRepository.update_notification_preferences",
        side_effect=update_notification_preferences,
    ), patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories_state,
    ):
        payload = {
            "user_id": 1,
            "categories": "",
            "keywords": "",
            "notify_via_email": False,
            "enabled": False,
        }
        res = client.post("/api/notifications/preferences", json=payload)
        print("\ntest_remove_all_notification_preferences:", res.get_json())
        assert res.status_code == 200
        assert "updated" in get_message(res)
