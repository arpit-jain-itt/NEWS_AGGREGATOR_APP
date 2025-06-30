import pytest
from unittest.mock import patch
from client.handlers.news_reporting_handler import NewsReportingHandler


@pytest.fixture
def handler():
    return NewsReportingHandler(current_user={"id": 1})


def test_list_reported_articles_with_data(handler):
    fake_reported = [
        {"article_id": 10, "report_count": 2},
        {"article_id": 11, "report_count": 1},
    ]
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json",
        side_effect=[fake_reported, fake_article],
    ), patch("builtins.input", side_effect=["1", "4"]):
        handler.list_reported_articles()
        print(
            "test_list_reported_articles_with_data: reported =",
            fake_reported,
            "article =",
            fake_article,
        )


def test_list_reported_articles_no_data(handler):
    with patch("client.handlers.news_reporting_handler.get_json", return_value=[]):
        handler.list_reported_articles()
        print("test_list_reported_articles_no_data: reported = []")


def test_manage_reported_article_show_details(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch("builtins.input", side_effect=["1", "4"]):
        handler.manage_reported_article(10)
        print("test_manage_reported_article_show_details: article =", fake_article)


def test_manage_reported_article_hide_success(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch(
        "builtins.input", side_effect=["2", "4"]
    ):
        handler.manage_reported_article(10)
        print("test_manage_reported_article_hide_success: article =", fake_article)


def test_manage_reported_article_hide_error(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch(
        "builtins.input", side_effect=["2", "4"]
    ):
        handler.manage_reported_article(10)
        print("test_manage_reported_article_hide_error: article =", fake_article)


def test_manage_reported_article_unhide_success(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch(
        "builtins.input", side_effect=["3", "4"]
    ):
        handler.manage_reported_article(10)
        print("test_manage_reported_article_unhide_success: article =", fake_article)


def test_manage_reported_article_unhide_error(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch(
        "builtins.input", side_effect=["3", "4"]
    ):
        handler.manage_reported_article(10)
        print("test_manage_reported_article_unhide_error: article =", fake_article)


def test_list_blocked_articles_with_data(handler):
    fake_blocked = [
        {"id": 10, "title": "Blocked Article"},
        {"id": 11, "title": "Another Blocked"},
    ]
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json",
        side_effect=[fake_blocked, fake_article],
    ), patch("builtins.input", side_effect=["1", "3"]):
        handler.list_blocked_articles()
        print(
            "test_list_blocked_articles_with_data: blocked =",
            fake_blocked,
            "article =",
            fake_article,
        )


def test_list_blocked_articles_no_data(handler):
    with patch("client.handlers.news_reporting_handler.get_json", return_value=[]):
        handler.list_blocked_articles()
        print("test_list_blocked_articles_no_data: blocked = []")


def test_manage_blocked_article_show_details(handler):
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch("builtins.input", side_effect=["1", "3"]):
        handler.manage_blocked_article(10)
        print("test_manage_blocked_article_show_details: article =", fake_article)


def test_manage_blocked_article_unhide_success(handler):
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch(
        "builtins.input", side_effect=["2", "3"]
    ):
        handler.manage_blocked_article(10)
        print("test_manage_blocked_article_unhide_success: article =", fake_article)


def test_manage_blocked_article_unhide_error(handler):
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": True}
    with patch(
        "client.handlers.news_reporting_handler.get_json", return_value=fake_article
    ), patch(
        "client.handlers.news_reporting_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch(
        "builtins.input", side_effect=["2", "3"]
    ):
        handler.manage_blocked_article(10)
        print("test_manage_blocked_article_unhide_error: article =", fake_article)


def test_list_my_reported_articles_with_data(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
        {"article_id": 11, "reason": "offensive", "created_at": "2024-06-29T13:00:00"},
    ]
    fake_article = {"id": 10, "title": "Reported Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json",
        side_effect=[fake_reports, fake_article],
    ), patch("builtins.input", side_effect=["1", "2"]):
        handler.list_my_reported_articles()
        print(
            "test_list_my_reported_articles_with_data: reports =",
            fake_reports,
            "article =",
            fake_article,
        )


def test_list_my_reported_articles_no_data(handler):
    with patch("client.handlers.news_reporting_handler.get_json", return_value=[]):
        handler.list_my_reported_articles()
        print("test_list_my_reported_articles_no_data: reports = []")


def test_unreport_article_success(handler):
    with patch(
        "client.handlers.news_reporting_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ):
        handler.unreport_article(10)
        print("test_unreport_article_success: status_code = 200")


def test_unreport_article_error(handler):
    with patch(
        "client.handlers.news_reporting_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ):
        handler.unreport_article(10)
        print("test_unreport_article_error: status_code = 500")
