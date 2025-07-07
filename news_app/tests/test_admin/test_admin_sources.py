import pytest
from datetime import datetime
from unittest.mock import patch
from server.models.source_model import Source

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_sources_state():
    return [
        Source(
            id=1,
            name="newsapi.org",
            api_endpoint="https://newsapi.org/v2/top-headlines",
            api_key="dummykey1",
            active=True,
            last_accessed=datetime(2025, 6, 29, 12, 0, 0),
        ),
        Source(
            id=2,
            name="thenewsapi.org",
            api_endpoint="https://thenewsapi.org/v1/news",
            api_key="dummykey2",
            active=False,
            last_accessed=datetime(2025, 6, 29, 12, 0, 0),
        ),
    ]


def test_list_sources(client, fake_sources_state):
    with patch(
        "server.repository.source_repository.SourceRepository.get_all_sources",
        return_value=fake_sources_state,
    ):
        res = client.get("/api/admin/news-sources", headers=ADMIN_HEADERS)
        print("\ntest_list_sources:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["name"] == "newsapi.org"


def test_add_source(client, fake_sources_state):
    def add_source(name):
        fake_sources_state.append(
            Source(
                id=len(fake_sources_state) + 1,
                name=name,
                api_endpoint="https://example.com",
                api_key="dummykey",
                active=True,
                last_accessed="2024-06-29T12:00:00",
            )
        )
        return True

    with patch(
        "server.repository.source_repository.SourceRepository.add_source",
        side_effect=add_source,
    ):
        res = client.post(
            "/api/admin/news-sources", json={"name": "Reuters"}, headers=ADMIN_HEADERS
        )
        print("\ntest_add_source:", res.get_json())
        assert res.status_code == 201
        assert "Source added" in res.get_json().get("message", "")
        print("Sources after add:", [s.name for s in fake_sources_state])


def test_remove_source(client, fake_sources_state):
    def remove_source(source_id):
        before = len(fake_sources_state)
        fake_sources_state[:] = [
            s for s in fake_sources_state if s.id != int(source_id)
        ]
        after = len(fake_sources_state)
        return before != after

    with patch(
        "server.repository.source_repository.SourceRepository.remove_source",
        side_effect=remove_source,
    ):
        res = client.delete("/api/admin/news-sources/1", headers=ADMIN_HEADERS)
        print("\ntest_remove_source:", res.get_json())
        assert res.status_code == 200
        assert "removed" in res.get_json().get("message", "")
        print("Sources after remove:", [s.name for s in fake_sources_state])


def test_set_active_source(client, fake_sources_state):
    def set_active_source(source_id):
        for s in fake_sources_state:
            s.active = s.id == int(source_id)
        return True

    with patch(
        "server.repository.source_repository.SourceRepository.set_active_source",
        side_effect=set_active_source,
    ):
        res = client.post(
            "/api/admin/set-active-source", json={"source_id": 2}, headers=ADMIN_HEADERS
        )
        print("\ntest_set_active_source:", res.get_json())
        assert res.status_code == 200
        assert "Active source updated" in res.get_json().get("message", "")
        print(
            "Sources after set active:",
            [(s.name, s.active) for s in fake_sources_state],
        )
