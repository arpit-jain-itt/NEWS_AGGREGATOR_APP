import pytest
from unittest.mock import patch
from client.handlers.notification_handler import NotificationHandler


@pytest.fixture
def handler():
    return NotificationHandler(current_user={"id": 1})


def test_manage_notifications_update_success(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }
    fake_categories = [{"name": "general"}, {"name": "sports"}]

    class FakeResp:
        ok = True

    with patch(
        "client.handlers.notification_handler.get_json",
        side_effect=[fake_prefs, fake_categories],
    ), patch(
        "client.handlers.notification_handler.post_json", return_value=FakeResp()
    ), patch(
        "builtins.input", side_effect=["y", "general", "tesla", "y", "y"]
    ):
        handler.manage_notifications()
        print(
            "test_manage_notifications_update_success: prefs =",
            fake_prefs,
            "categories =",
            fake_categories,
        )


def test_manage_notifications_update_error(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }
    fake_categories = [{"name": "general"}, {"name": "sports"}]

    class FakeResp:
        ok = False

    with patch(
        "client.handlers.notification_handler.get_json",
        side_effect=[fake_prefs, fake_categories],
    ), patch(
        "client.handlers.notification_handler.post_json", return_value=FakeResp()
    ), patch(
        "builtins.input", side_effect=["y", "general", "tesla", "y", "y"]
    ):
        handler.manage_notifications()
        print(
            "test_manage_notifications_update_error: prefs =",
            fake_prefs,
            "categories =",
            fake_categories,
        )


def test_manage_notifications_remove_all_success(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }

    class FakeResp:
        ok = True

    with patch(
        "client.handlers.notification_handler.get_json", return_value=fake_prefs
    ), patch(
        "client.handlers.notification_handler.post_json", return_value=FakeResp()
    ), patch(
        "builtins.input", side_effect=["n", "y"]
    ):
        handler.manage_notifications()
        print("test_manage_notifications_remove_all_success: prefs =", fake_prefs)


def test_manage_notifications_remove_all_error(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }

    class FakeResp:
        ok = False

    with patch(
        "client.handlers.notification_handler.get_json", return_value=fake_prefs
    ), patch(
        "client.handlers.notification_handler.post_json", return_value=FakeResp()
    ), patch(
        "builtins.input", side_effect=["n", "y"]
    ):
        handler.manage_notifications()
        print("test_manage_notifications_remove_all_error: prefs =", fake_prefs)


def test_manage_notifications_no_changes(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }
    with patch(
        "client.handlers.notification_handler.get_json", return_value=fake_prefs
    ), patch("builtins.input", side_effect=["n", "n"]):
        handler.manage_notifications()
        print("test_manage_notifications_no_changes: prefs =", fake_prefs)


def test_manage_notifications_invalid_category(handler):
    fake_prefs = {
        "categories": ["general"],
        "keywords": ["tesla"],
        "notify_via_email": True,
        "enabled": True,
    }
    fake_categories = [{"name": "general"}, {"name": "sports"}]

    class FakeResp:
        ok = True

    with patch(
        "client.handlers.notification_handler.get_json",
        side_effect=[fake_prefs, fake_categories],
    ), patch(
        "client.handlers.notification_handler.post_json", return_value=FakeResp()
    ), patch(
        "builtins.input", side_effect=["y", "invalidcat", "tesla", "y", "y"]
    ):
        handler.manage_notifications()
        print(
            "test_manage_notifications_invalid_category: prefs =",
            fake_prefs,
            "categories =",
            fake_categories,
        )
