import pytest
from unittest.mock import patch
from server.models.keyword_filter_model import KeywordFilter

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_keywords_state():
    # Start with two keywords
    return [
        KeywordFilter(
            id=1,
            keyword="blockme",
            active=True,
            created_at="2024-06-29T12:00:00",
            updated_at="2024-06-29T12:00:00",
        ),
        KeywordFilter(
            id=2,
            keyword="test",
            active=False,
            created_at="2024-06-29T12:00:00",
            updated_at="2024-06-29T12:00:00",
        ),
    ]


def test_list_keywords(client, fake_keywords_state):
    with patch(
        "server.services.admin_service.AdminService.get_all_keywords",
        return_value=fake_keywords_state,
    ):
        res = client.get("/api/admin/keywords", headers=ADMIN_HEADERS)
        print("\ntest_list_keywords:", res.get_json())
        data = res.get_json()["data"]
        print("Current keywords:", [k.keyword for k in fake_keywords_state])
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["keyword"] == "blockme"


def test_add_keyword(client, fake_keywords_state):
    def add_keyword_filter(keyword):
        fake_keywords_state.append(
            KeywordFilter(
                id=len(fake_keywords_state) + 1,
                keyword=keyword,
                active=True,
                created_at="2024-06-29T12:00:00",
                updated_at="2024-06-29T12:00:00",
            )
        )
        return True

    with patch(
        "server.services.admin_service.AdminService.add_keyword_filter",
        side_effect=add_keyword_filter,
    ):
        res = client.post(
            "/api/admin/keywords", json={"keyword": "newword"}, headers=ADMIN_HEADERS
        )
        print("\ntest_add_keyword:", res.get_json())
        print("Current keywords after add:", [k.keyword for k in fake_keywords_state])
        assert res.status_code == 201
        assert "Keyword added" in res.get_json().get("message", "")


def test_block_keyword(client, fake_keywords_state):
    def block_keyword(keyword):
        for k in fake_keywords_state:
            if k.keyword == keyword:
                k.active = True
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.block_keyword",
        side_effect=block_keyword,
    ):
        res = client.post(
            "/api/admin/block-keyword",
            json={"keyword": "blockme"},
            headers=ADMIN_HEADERS,
        )
        print("\ntest_block_keyword:", res.get_json())
        print(
            "Current keywords after block:",
            [(k.keyword, k.active) for k in fake_keywords_state],
        )
        assert res.status_code == 200
        assert "blocked" in res.get_json().get("message", "")


def test_unblock_keyword(client, fake_keywords_state):
    def unblock_keyword(keyword):
        for k in fake_keywords_state:
            if k.keyword == keyword:
                k.active = False
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.unblock_keyword",
        side_effect=unblock_keyword,
    ):
        res = client.post(
            "/api/admin/unblock-keyword",
            json={"keyword": "blockme"},
            headers=ADMIN_HEADERS,
        )
        print("\ntest_unblock_keyword:", res.get_json())
        print(
            "Current keywords after unblock:",
            [(k.keyword, k.active) for k in fake_keywords_state],
        )
        assert res.status_code == 200
        assert "unblocked" in res.get_json().get("message", "")


def test_delete_keyword(client, fake_keywords_state):
    def delete_keyword(keyword):
        before = len(fake_keywords_state)
        fake_keywords_state[:] = [
            k for k in fake_keywords_state if k.keyword != keyword
        ]
        after = len(fake_keywords_state)
        return before != after

    with patch(
        "server.services.admin_service.AdminService.delete_keyword",
        side_effect=delete_keyword,
    ):
        res = client.post(
            "/api/admin/delete-keyword",
            json={"keyword": "blockme"},
            headers=ADMIN_HEADERS,
        )
        print("\ntest_delete_keyword:", res.get_json())
        print(
            "Current keywords after delete:", [k.keyword for k in fake_keywords_state]
        )
        assert res.status_code == 200
        assert "deleted" in res.get_json().get("message", "")
