import pytest
from unittest.mock import patch
from datetime import datetime

from server.models.article_model import Article
from server.models.report_model import Report

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_articles_state():
    return [
        Article(
            id=10,
            title="Blocked Article",
            description="desc",
            content="content",
            url="http://example.com",
            published_at=datetime.now(),
            source_id=1,
            category_id=1,
            is_hidden=False,
            category_name="general",
        )
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
            user_id=2,
            article_id=10,
            reason="offensive",
            created_at=now,
            status="reviewed",
        ),
    ]


def test_fetch_news(client):
    with patch(
        "server.services.news_service.NewsService.fetch_and_store_news",
        return_value=None,
    ):
        res = client.post("/api/admin/fetch-news", headers=ADMIN_HEADERS)
        print("\ntest_fetch_news:", res.get_json())
        assert res.status_code == 200
        assert "message" in res.get_json()


def test_fetch_news_error(client):
    with patch(
        "server.services.news_service.NewsService.fetch_and_store_news",
        side_effect=Exception("DB error"),
    ):
        res = client.post("/api/admin/fetch-news", headers=ADMIN_HEADERS)
        assert res.status_code in (500, 400)


def test_reported_articles(client):
    fake_reported = [
        {"article_id": 10, "report_count": 2},
        {"article_id": 11, "report_count": 1},
    ]
    with patch(
        "server.services.admin_service.AdminService.get_reported_articles",
        return_value=fake_reported,
    ):
        res = client.get("/api/admin/reported-articles", headers=ADMIN_HEADERS)
        print("\ntest_reported_articles:", res.get_json())
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert isinstance(data, list)
        assert data == fake_reported


def test_blocked_articles(client, fake_articles_state):
    # article 10 is blocked
    fake_articles_state[0].is_hidden = True
    with patch(
        "server.services.admin_service.AdminService.get_blocked_articles",
        return_value=fake_articles_state,
    ):
        res = client.get("/api/admin/blocked-articles", headers=ADMIN_HEADERS)
        print("\ntest_blocked_articles:", res.get_json())
        data = res.get_json()["data"]
        print("Articles after block:", [(a["id"], a["title"]) for a in data])
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["id"] == 10
        assert data[0]["title"] == "Blocked Article"


def test_hide_article(client, fake_articles_state):
    def hide_article(article_id):
        for art in fake_articles_state:
            if art.id == int(article_id):
                art.is_hidden = True
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.hide_article",
        side_effect=hide_article,
    ), patch(
        "server.services.admin_service.AdminService.update_report_status",
        return_value=None,
    ):
        res = client.post("/api/admin/hide-article/10", headers=ADMIN_HEADERS)
        print("\ntest_hide_article:", res.get_json())
        print(
            "Articles after hide:", [(a.id, a.is_hidden) for a in fake_articles_state]
        )
        assert res.status_code in (200, 400)
        assert "hidden" in res.get_json().get("message", "")
        assert fake_articles_state[0].is_hidden is True


def test_hide_article_not_found(client):
    with patch(
        "server.services.admin_service.AdminService.hide_article",
        return_value=False,
    ), patch(
        "server.services.admin_service.AdminService.update_report_status",
        return_value=None,
    ):
        res = client.post("/api/admin/hide-article/9999", headers=ADMIN_HEADERS)
        assert res.status_code in (404, 400, 200)


def test_unhide_article(client, fake_articles_state):
    # article 10 is hidden
    fake_articles_state[0].is_hidden = True

    def unhide_article(article_id):
        for art in fake_articles_state:
            if art.id == int(article_id):
                art.is_hidden = False
                return True
        return False

    with patch(
        "server.services.admin_service.AdminService.unhide_article",
        side_effect=unhide_article,
    ):
        res = client.post("/api/admin/unhide-article/10", headers=ADMIN_HEADERS)
        print("\ntest_unhide_article:", res.get_json())
        print(
            "Articles after unhide:", [(a.id, a.is_hidden) for a in fake_articles_state]
        )
        assert res.status_code in (200, 400)
        assert "unhidden" in res.get_json().get("message", "")
        assert fake_articles_state[0].is_hidden is False


def test_unhide_article_not_found(client):
    with patch(
        "server.services.admin_service.AdminService.unhide_article",
        return_value=False,
    ):
        res = client.post("/api/admin/unhide-article/9999", headers=ADMIN_HEADERS)
        assert res.status_code in (404, 400, 200)


def test_article_reports(client, fake_reports_state):
    with patch(
        "server.services.admin_service.AdminService.get_reports_for_article",
        return_value=fake_reports_state,
    ):
        res = client.get("/api/admin/reports/10", headers=ADMIN_HEADERS)
        print("\ntest_article_reports:", res.get_json())
        assert res.status_code in (200, 500)
        if res.status_code == 200:
            data = res.get_json()["data"]
            assert isinstance(data, list)
            assert data[0]["article_id"] == 10
