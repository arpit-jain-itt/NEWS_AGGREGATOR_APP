import pytest
from unittest.mock import patch
from server.models.category_model import Category

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_categories_state():
    return [
        Category(id=1, name="general", is_hidden=False),
        Category(id=2, name="sports", is_hidden=True),
    ]


def test_list_categories(client, fake_categories_state):
    with patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories_state,
    ):
        res = client.get("/api/categories")
        print("\ntest_list_categories:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["name"] == "general"


def test_admin_list_categories(client, fake_categories_state):
    with patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories_state,
    ):
        res = client.get("/api/categories/admin/categories", headers=ADMIN_HEADERS)
        print("\ntest_admin_list_categories:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[1]["is_hidden"] is True


def test_add_category(client, fake_categories_state):
    def add_category(name):
        if any(c.name == name for c in fake_categories_state):
            return False
        fake_categories_state.append(
            Category(id=len(fake_categories_state) + 1, name=name, is_hidden=False)
        )
        return True

    with patch(
        "server.repository.category_repository.CategoryRepository.add_category",
        side_effect=add_category,
    ):
        res = client.post(
            "/api/categories", json={"name": "tech"}, headers=ADMIN_HEADERS
        )
        print("\ntest_add_category:", res.get_json())
        assert res.status_code == 201
        assert "Category added" in res.get_json().get("message", "")
        print("Categories after add:", [c.name for c in fake_categories_state])


def test_add_duplicate_category(client, fake_categories_state):
    def add_category(name):
        return False

    with patch(
        "server.repository.category_repository.CategoryRepository.add_category",
        side_effect=add_category,
    ):
        res = client.post(
            "/api/categories", json={"name": "general"}, headers=ADMIN_HEADERS
        )
        print("\ntest_add_duplicate_category:", res.get_json())
        assert res.status_code == 409
        assert "already exists" in res.get_json().get("message", "")


def test_delete_category(client, fake_categories_state):
    def delete_category_by_id(category_id):
        before = len(fake_categories_state)
        fake_categories_state[:] = [
            c for c in fake_categories_state if c.id != category_id
        ]
        after = len(fake_categories_state)
        return before != after

    with patch(
        "server.repository.category_repository.CategoryRepository.delete_category_by_id",
        side_effect=delete_category_by_id,
    ):
        res = client.delete("/api/categories/1", headers=ADMIN_HEADERS)
        print("\ntest_delete_category:", res.get_json())
        assert res.status_code == 200
        assert "deleted" in res.get_json().get("message", "")
        print("Categories after delete:", [c.name for c in fake_categories_state])


def test_delete_nonexistent_category(client, fake_categories_state):
    def delete_category_by_id(category_id):
        return False

    with patch(
        "server.repository.category_repository.CategoryRepository.delete_category_by_id",
        side_effect=delete_category_by_id,
    ):
        res = client.delete("/api/categories/999", headers=ADMIN_HEADERS)
        print("\ntest_delete_nonexistent_category:", res.get_json())
        assert res.status_code == 404
        assert "not found" in res.get_json().get("message", "")
