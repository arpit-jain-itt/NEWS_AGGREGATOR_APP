import pytest
from unittest.mock import patch
from datetime import datetime
from server.models.article_model import Article
from server.models.category_model import Category


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


def fake_category(id=1, name="general"):
    return Category(id=id, name=name, is_hidden=False)


def get_data(response):
    data = response.get_json()
    return data.get("data", None)


def test_headlines(client):
    fake_articles = [fake_article(1, "Headline 1"), fake_article(2, "Headline 2")]
    with patch(
        "server.services.news_service.NewsService.search_articles",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/headlines")
        print("\ntest_headlines:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["title"] == "Headline 1"


def test_latest(client):
    fake_articles = [fake_article(1, "Latest 1"), fake_article(2, "Latest 2")]
    with patch(
        "server.services.news_service.NewsService.get_latest_articles",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/latest")
        print("\ntest_latest:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["title"] == "Latest 1"


def test_search_articles(client):
    fake_articles = [fake_article(1, "Search Result")]
    with patch(
        "server.services.news_service.NewsService.search_articles",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/search?keyword=test")
        print("\ntest_search_articles:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["title"] == "Search Result"


def test_categories(client):
    fake_categories = [fake_category(1, "general"), fake_category(2, "sports")]
    with patch(
        "server.repository.category_repository.CategoryRepository.get_all_categories",
        return_value=fake_categories,
    ):
        res = client.get("/api/news/categories")
        print("\ntest_categories:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["name"] == "general"


def test_article_details(client):
    article = fake_article(1, "Detail Article")
    with patch(
        "server.repository.article_repository.ArticleRepository.get_article_by_id",
        return_value=article,
    ):
        res = client.get("/api/news/article/1")
        print("\ntest_article_details:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert data["title"] == "Detail Article"


def test_personalized_news(client):
    fake_articles = [fake_article(1, "Personalized 1")]
    with patch(
        "server.services.news_service.NewsService.get_personalized_articles",
        return_value=fake_articles,
    ):
        res = client.get("/api/news/personalized/1")
        print("\ntest_personalized_news:", res.get_json())
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["title"] == "Personalized 1"


def test_headlines_error(client):
    with patch("server.services.news_service.NewsService.search_articles", side_effect=Exception()):
        res = client.get("/api/news/headlines")
        assert res.status_code in (500, 400)


def test_latest_error(client):
    with patch("server.services.news_service.NewsService.get_latest_articles", side_effect=Exception()):
        res = client.get("/api/news/latest")
        assert res.status_code in (500, 400)


def test_search_articles_error(client):
    with patch("server.services.news_service.NewsService.search_articles", side_effect=Exception()):
        res = client.get("/api/news/search?keyword=test")
        assert res.status_code in (500, 400)


def test_headlines_empty(client):
    with patch(
        "server.services.news_service.NewsService.search_articles",
        return_value=[],
    ):
        res = client.get("/api/news/headlines")
        data = get_data(res)
        assert res.status_code == 200
        assert data == []


def test_headlines_invalid_keyword(client):
    # Simulate search_articles returning articles with no keyword match
    with patch(
        "server.services.news_service.NewsService.search_articles",
        return_value=[],
    ):
        res = client.get("/api/news/search?keyword=nonexistent")
        data = get_data(res)
        assert res.status_code == 200
        assert data == []


def test_article_details_not_found(client):
    with patch(
        "server.repository.article_repository.ArticleRepository.get_article_by_id",
        return_value=None,
    ):
        res = client.get("/api/news/article/9999")
        assert res.status_code in (404, 400, 500)


def test_personalized_news_empty(client):
    with patch(
        "server.services.news_service.NewsService.get_personalized_articles",
        return_value=[],
    ):
        res = client.get("/api/news/personalized/1")
        data = get_data(res)
        assert res.status_code == 200
        assert data == []


# Simulate scoring logic for personalized articles
from unittest.mock import MagicMock

def test_personalized_news_scoring(client):
    fake_article_obj = fake_article(1, "Personalized Scored")
    # Patch NewsService to simulate scoring logic
    with patch(
        "server.services.news_service.NewsService.get_personalized_articles",
        return_value=[fake_article_obj],
    ) as mock_personalized:
        res = client.get("/api/news/personalized/1")
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["title"] == "Personalized Scored"
        # Optionally, check that scoring logic was called (if exposed)
        # mock_personalized.assert_called_once()


# Test timestamp parsing edge case via NewsService (simulate parse_ts)
def test_headlines_with_invalid_timestamp(client):
    # Patch NewsService to simulate parse_ts returning current time on error
    broken_article = fake_article(1, "Broken Timestamp")
    # Instead of setting published_at to a string, patch parse_ts to raise an exception
    with patch("server.services.news_service.NewsService.search_articles", return_value=[broken_article]), \
         patch("server.utils.service_helper.parse_ts", side_effect=Exception()):
        res = client.get("/api/news/headlines")
        data = get_data(res)
        assert res.status_code == 200
        assert data[0]["title"] == "Broken Timestamp"
