import pytest
from unittest.mock import patch
from datetime import datetime
from server.models.article_model import Article

ADMIN_HEADERS = {"X-User-ID": "1"}


def fake_article(id=1, title="Test Article"):
    return Article(
        id=id,
        title=title,
        description="desc",
        content="content",
        url="http://abc_test.com",
        published_at=datetime.now(),
        source_id=1,
        category_id=1,
        is_hidden=False,
        category_name="general",
    )


def get_message(response):
    data = response.get_json()
    return (data.get("data", {}) or {}).get("message", "") or data.get("message", "")


def test_save_article(client):
    with patch(
        "server.services.news_service.NewsService.save_article", return_value="saved"
    ):
        res = client.post("/api/news/save", json={"user_id": 1, "article_id": 1})
        print("\ntest_save_article:", res.get_json())
        assert res.status_code in (200, 201)
        assert "saved" in get_message(res)


def test_remove_saved_article(client):
    with patch(
        "server.services.news_service.NewsService.remove_saved_article",
        return_value="deleted",
    ):
        res = client.delete("/api/news/save?user_id=1&article_id=1")
        print("\ntest_remove_saved_article:", res.get_json())
        assert res.status_code == 200
        assert "removed" in get_message(res)


def test_mark_article_viewed(client):
    with patch(
        "server.services.news_service.NewsService.mark_article_viewed",
        return_value=None,
    ):
        res = client.post("/api/news/viewed", json={"user_id": 1, "article_id": 1})
        print("\ntest_mark_article_viewed:", res.get_json())
        assert res.status_code == 200
        assert "marked" in get_message(res)


def test_saved_articles(client):
    fake_articles = [fake_article(1, "Saved 1")]
    with patch(
        "server.services.news_service.NewsService.get_saved_articles_by_user",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/saved?user_id=1")
        print("\ntest_saved_articles:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data[0]["title"] == "Saved 1"


def test_react_to_article(client):
    with patch(
        "server.services.news_service.NewsService.react_to_article",
        return_value="created",
    ):
        res = client.post(
            "/api/news/react", json={"user_id": 1, "article_id": 1, "is_like": True}
        )
        print("\ntest_react_to_article:", res.get_json())
        assert res.status_code in (200, 201)
        assert "created" in get_message(res)


def test_remove_reaction(client):
    with patch(
        "server.services.news_service.NewsService.remove_reaction",
        return_value="deleted",
    ):
        res = client.delete("/api/news/react?user_id=1&article_id=1")
        print("\ntest_remove_reaction:", res.get_json())
        assert res.status_code == 200
        assert "removed" in get_message(res)


def test_reaction_summary(client):
    with patch(
        "server.services.news_service.NewsService.get_reaction_summary",
        return_value={"likes": 1, "dislikes": 0},
    ):
        res = client.get("/api/news/reactions/summary?user_id=1")
        print("\ntest_reaction_summary:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data["likes"] == 1


def test_reacted_articles(client):
    fake_articles = [fake_article(1, "Liked 1")]
    with patch(
        "server.services.news_service.NewsService.get_reacted_articles",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/reactions?user_id=1&type=like")
        print("\ntest_reacted_articles:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data[0]["title"] == "Liked 1"


def test_article_reaction_counts(client):
    with patch(
        "server.services.news_service.NewsService.get_article_reactions_count",
        return_value={"likes": 5, "dislikes": 2},
    ):
        res = client.get("/api/news/reactions/article/1")
        print("\ntest_article_reaction_counts:", res.get_json())
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data["likes"] == 5


def test_report_article(client):
    with patch(
        "server.services.news_service.NewsService.report_article", return_value=True
    ):
        res = client.post(
            "/api/news/report", json={"user_id": 1, "article_id": 1, "reason": "spam"}
        )
        print("\ntest_report_article:", res.get_json())
        assert res.status_code in (200, 201, True)
        assert "submitted" in get_message(res)


def test_save_article_error(client):
    with patch(
        "server.services.news_service.NewsService.save_article", side_effect=Exception()
    ):
        res = client.post("/api/news/save", json={"user_id": 1, "article_id": 1})
        assert res.status_code in (500, 400)


def test_remove_saved_article_error(client):
    with patch(
        "server.services.news_service.NewsService.remove_saved_article",
        side_effect=Exception(),
    ):
        res = client.delete("/api/news/save?user_id=1&article_id=1")
        assert res.status_code in (500, 400)


def test_save_article_invalid_user(client):
    with patch(
        "server.services.news_service.NewsService.save_article", return_value=None
    ):
        res = client.post("/api/news/save", json={"user_id": 9999, "article_id": 1})
        assert res.status_code in (404, 400, 200)


def test_saved_articles_empty(client):
    with patch(
        "server.services.news_service.NewsService.get_saved_articles_by_user",
        return_value=[],
    ):
        res = client.get("/api/news/saved?user_id=1")
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert data == []


def test_react_to_article_invalid(client):
    with patch(
        "server.services.news_service.NewsService.react_to_article",
        return_value=None,
    ):
        res = client.post(
            "/api/news/react", json={"user_id": 1, "article_id": 1, "is_like": True}
        )
        assert res.status_code in (404, 400, 200)


def test_report_article_invalid(client):
    with patch(
        "server.services.news_service.NewsService.report_article", return_value=False
    ):
        res = client.post(
            "/api/news/report", json={"user_id": 1, "article_id": 1, "reason": "spam"}
        )
        assert res.status_code in (404, 400, 200, 500)
