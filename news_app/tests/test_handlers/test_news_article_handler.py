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


def test_view_article_missing_id(handler):
    with patch("client.handlers.news_article_handler.print_article_details"), \
         patch("builtins.input") as mock_input:
        handler.view_article({})
        mock_input.assert_not_called()


def test_article_action_menu_save(handler):
    with patch("builtins.input", return_value="1"), \
         patch.object(handler, "_save_article") as mock_save:
        handler._article_action_menu(1)
        mock_save.assert_called_once_with(1)


def test_article_action_menu_like(handler):
    with patch("builtins.input", return_value="2"), \
         patch.object(handler, "_react_to_article") as mock_react:
        handler._article_action_menu(1)
        mock_react.assert_called_once_with(1, True)


def test_article_action_menu_dislike(handler):
    with patch("builtins.input", return_value="3"), \
         patch.object(handler, "_react_to_article") as mock_react:
        handler._article_action_menu(1)
        mock_react.assert_called_once_with(1, False)


def test_article_action_menu_report(handler):
    with patch("builtins.input", return_value="4"), \
         patch.object(handler, "report_article") as mock_report:
        handler._article_action_menu(1)
        mock_report.assert_called_once_with(1)


def test_article_action_menu_back(handler):
    with patch("builtins.input", return_value="5"):
        handler._article_action_menu(1)  # Should just return, no error


def test_react_to_article_none_response(handler):
    with patch("client.handlers.news_article_handler.post_json", return_value=None):
        handler._react_to_article(1, True)


def test_react_to_article_error_status(handler):
    class FakeResp:
        status_code = 500
    with patch("client.handlers.news_article_handler.post_json", return_value=FakeResp()):
        handler._react_to_article(1, True)


def test_save_article_none_response(handler):
    with patch("client.handlers.news_article_handler.post_json", return_value=None):
        handler._save_article(1)


def test_save_article_error_status(handler):
    class FakeResp:
        status_code = 500
    with patch("client.handlers.news_article_handler.post_json", return_value=FakeResp()):
        handler._save_article(1)


def test_remove_saved_article_none_response(handler):
    with patch("client.handlers.news_article_handler.delete_json", return_value=None):
        handler._remove_saved_article(1)


def test_remove_saved_article_error_status(handler):
    class FakeResp:
        status_code = 500
    with patch("client.handlers.news_article_handler.delete_json", return_value=FakeResp()):
        handler._remove_saved_article(1)


def test_report_article_none_response(handler):
    with patch("builtins.input", return_value="spam"), \
         patch("client.handlers.news_article_handler.post_json", return_value=None):
        handler.report_article(1)


def test_report_article_error_status(handler):
    class FakeResp:
        status_code = 404
    with patch("builtins.input", return_value="spam"), \
         patch("client.handlers.news_article_handler.post_json", return_value=FakeResp()):
        handler.report_article(1)


def test_list_news_no_categories(handler):
    with patch("client.handlers.news_article_handler.get_json", return_value=[]):
        handler.list_news()


def test_list_news_invalid_input(handler):
    fake_categories = [{"name": "business"}]
    with patch("client.handlers.news_article_handler.get_json", return_value=fake_categories), \
         patch("builtins.input", return_value="not_a_number"):
        handler.list_news()


def test_list_news_invalid_selection(handler):
    fake_categories = [{"name": "business"}]
    with patch("client.handlers.news_article_handler.get_json", return_value=fake_categories), \
         patch("builtins.input", return_value="5"):
        handler.list_news()


def test_view_saved_article_missing_id(handler):
    with patch("client.handlers.news_article_handler.print_article_details"), \
         patch("builtins.input") as mock_input:
        handler.view_saved_article({})
        mock_input.assert_not_called()


def test_saved_article_action_menu_remove(handler):
    with patch("builtins.input", return_value="1"), \
         patch.object(handler, "_remove_saved_article") as mock_remove:
        handler._saved_article_action_menu(1)
        mock_remove.assert_called_once_with(1)


def test_saved_article_action_menu_like(handler):
    with patch("builtins.input", return_value="2"), \
         patch.object(handler, "_react_to_article") as mock_react:
        handler._saved_article_action_menu(1)
        mock_react.assert_called_once_with(1, True)


def test_saved_article_action_menu_dislike(handler):
    with patch("builtins.input", return_value="3"), \
         patch.object(handler, "_react_to_article") as mock_react:
        handler._saved_article_action_menu(1)
        mock_react.assert_called_once_with(1, False)


def test_saved_article_action_menu_back(handler):
    with patch("builtins.input", return_value="4"):
        handler._saved_article_action_menu(1)  # Should just return, no error


def test_search_articles_no_filters(handler):
    with patch("builtins.input", side_effect=["", ""]):
        handler.search_articles()
