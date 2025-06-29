import pytest
from unittest.mock import patch

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_categories_state():
    # Start with one category
    return [
        {
            "id": 1,
            "name": "general",
            "is_hidden": False,
        }
    ]


def test_hide_category(client, fake_categories_state):
    def hide_category(category_id):
        for cat in fake_categories_state:
            if cat["id"] == int(category_id):
                cat["is_hidden"] = True
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.hide_category",
        side_effect=hide_category,
    ):
        res = client.post("/api/admin/hide-category/1", headers=ADMIN_HEADERS)
        print("\ntest_hide_category:", res.get_json())
        print("Categories after hide:", fake_categories_state)
        assert res.status_code in (200, 400)
        assert "hidden" in res.get_json().get("message", "")
        assert fake_categories_state[0]["is_hidden"] is True


def test_unhide_category(client, fake_categories_state):
    # Simulate that category 1 is hidden
    fake_categories_state[0]["is_hidden"] = True

    def unhide_category(category_id):
        for cat in fake_categories_state:
            if cat["id"] == int(category_id):
                cat["is_hidden"] = False
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.unhide_category",
        side_effect=unhide_category,
    ):
        res = client.post("/api/admin/unhide-category/1", headers=ADMIN_HEADERS)
        print("\ntest_unhide_category:", res.get_json())
        print("Categories after unhide:", fake_categories_state)
        assert res.status_code in (200, 400)
        assert "unhidden" in res.get_json().get("message", "")
        assert fake_categories_state[0]["is_hidden"] is False
