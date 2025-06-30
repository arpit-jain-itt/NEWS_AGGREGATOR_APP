import pytest
from unittest.mock import patch
from client.handlers.news_article_handler import NewsArticleHandler


@pytest.fixture
def handler():
    return NewsArticleHandler(current_user={"id": 1})


def test_view_headlines(handler):
    fake_articles = [
        {"id": 1, "title": "Fake News 1"},
        {"id": 2, "title": "Fake News 2"},
    ]
    with patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ), patch("builtins.input", side_effect=["b"]):
        handler.view_headlines()
        print("test_view_headlines: articles =", fake_articles)


def test_list_personalized_articles(handler):
    fake_articles = [{"id": 1, "title": "Personalized News"}]
    with patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ), patch("builtins.input", side_effect=["b"]):
        handler.list_personalized_articles()
        print("test_list_personalized_articles: articles =", fake_articles)


def test_save_article_success(handler):
    with patch(
        "client.handlers.news_article_handler.post_json",
        return_value=type("Resp", (), {"status_code": 201})(),
    ):
        handler._save_article(1)
        print("test_save_article_success: status_code = 201")


def test_save_article_error(handler):
    with patch(
        "client.handlers.news_article_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ):
        handler._save_article(1)
        print("test_save_article_error: status_code = 500")


def test_remove_saved_article_success(handler):
    with patch(
        "client.handlers.news_article_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ):
        handler._remove_saved_article(1)
        print("test_remove_saved_article_success: status_code = 200")


def test_remove_saved_article_error(handler):
    with patch(
        "client.handlers.news_article_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ):
        handler._remove_saved_article(1)
        print("test_remove_saved_article_error: status_code = 500")


def test_report_article_no_reason(handler):
    with patch("builtins.input", return_value=""):
        handler.report_article(1)
        print("test_report_article_no_reason: input was empty")


def test_report_article_success(handler):
    with patch(
        "client.handlers.news_article_handler.post_json",
        return_value=type("Resp", (), {"status_code": 201})(),
    ), patch("builtins.input", return_value="spam"):
        handler.report_article(1)
        print("test_report_article_success: input was 'spam', status_code = 201")


def test_report_article_error(handler):
    def error_post_json(*args, **kwargs):
        class Resp:
            status_code = 500

        return Resp()

    with patch(
        "client.handlers.news_article_handler.post_json", error_post_json
    ), patch("builtins.input", return_value="spam"):
        handler.report_article(1)
        print("test_report_article_error: input was 'spam', status_code = 500")


def test_list_saved_articles(handler):
    fake_articles = [{"id": 1, "title": "Saved 1"}]
    with patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ), patch("builtins.input", side_effect=["b"]):
        handler.list_saved_articles()
        print("test_list_saved_articles: articles =", fake_articles)


def test_list_liked_articles(handler):
    fake_articles = [{"id": 1, "title": "Liked 1"}]
    with patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ), patch("builtins.input", side_effect=["b"]):
        handler.list_liked_articles()
        print("test_list_liked_articles: articles =", fake_articles)


def test_list_disliked_articles(handler):
    fake_articles = [{"id": 1, "title": "Disliked 1"}]
    with patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ), patch("builtins.input", side_effect=["b"]):
        handler.list_disliked_articles()
        print("test_list_disliked_articles: articles =", fake_articles)


def test_list_news(handler):
    fake_categories = [{"name": "business"}, {"name": "sports"}]
    fake_articles = [
        {"id": 1, "title": "Fake News 1"},
        {"id": 2, "title": "Fake News 2"},
    ]
    with patch(
        "client.handlers.news_article_handler.get_json",
        side_effect=[fake_categories, fake_articles],
    ), patch("builtins.input", side_effect=["1"] + ["b"] * 10):
        handler.list_news()
        print(
            "test_list_news: categories =", fake_categories, "articles =", fake_articles
        )


def test_search_articles(handler):
    fake_articles = [{"id": 1, "title": "Search Result"}]
    with patch("builtins.input", side_effect=["test", ""] + ["b"] * 10), patch(
        "client.handlers.news_article_handler.get_json", return_value=fake_articles
    ):
        handler.search_articles()
        print("test_search_articles: articles =", fake_articles)
