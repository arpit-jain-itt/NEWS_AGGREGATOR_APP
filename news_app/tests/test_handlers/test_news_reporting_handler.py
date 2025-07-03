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


def test_list_reported_articles_invalid_input(handler):
    fake_reported = [
        {"article_id": 10, "report_count": 2},
    ]
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_reported), \
         patch("builtins.input", side_effect=["invalid", "b"]):
        handler.list_reported_articles()


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


def test_manage_reported_article_invalid_choice(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_article), \
         patch("builtins.input", side_effect=["9", "4"]):
        handler.manage_reported_article(10)


def test_manage_reported_article_hide_none_response(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": False}
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_article), \
         patch("client.handlers.news_reporting_handler.post_json", return_value=None), \
         patch("builtins.input", side_effect=["2", "4"]):
        handler.manage_reported_article(10)


def test_manage_reported_article_unhide_none_response(handler):
    fake_article = {"id": 10, "title": "Test Article", "is_hidden": True}
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_article), \
         patch("client.handlers.news_reporting_handler.post_json", return_value=None), \
         patch("builtins.input", side_effect=["3", "4"]):
        handler.manage_reported_article(10)


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


def test_list_blocked_articles_invalid_input(handler):
    fake_blocked = [
        {"id": 10, "title": "Blocked Article"},
    ]
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_blocked), \
         patch("builtins.input", side_effect=["invalid", "b"]):
        handler.list_blocked_articles()


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


def test_manage_blocked_article_already_unhidden(handler):
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": False}
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_article), \
         patch("builtins.input", side_effect=["2", "3"]):
        handler.manage_blocked_article(10)


def test_manage_blocked_article_invalid_option(handler):
    fake_article = {"id": 10, "title": "Blocked Article", "is_hidden": True}
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_article), \
         patch("builtins.input", side_effect=["9", "3"]):
        handler.manage_blocked_article(10)


def test_manage_blocked_article_article_fetch_none(handler):
    with patch("client.handlers.news_reporting_handler.get_json", return_value=None):
        handler.manage_blocked_article(10)


def test_show_reported_article_details_article_none(handler):
    with patch("client.handlers.news_reporting_handler.get_json", return_value=None):
        handler.show_reported_article_details(10)


def test_list_my_reported_articles_with_data(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
        {"article_id": 11, "reason": "offensive", "created_at": "2024-06-29T13:00:00"},
    ]
    fake_article = {"id": 10, "title": "Reported Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json",
        side_effect=[fake_reports, fake_article],
    ), patch("builtins.input", side_effect=["1", "2", "b"]):
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


def test_list_my_reported_articles_invalid_input(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
    ]
    with patch("client.handlers.news_reporting_handler.get_json", return_value=fake_reports), \
         patch("builtins.input", side_effect=["invalid", "b"]):
        handler.list_my_reported_articles()


def test_list_my_reported_articles_article_fetch_none(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
    ]
    with patch("client.handlers.news_reporting_handler.get_json", side_effect=[fake_reports, None]), \
         patch("builtins.input", side_effect=["1", "b"]):
        handler.list_my_reported_articles()


def test_list_my_reported_articles_submenu_go_back(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
    ]
    fake_article = {"id": 10, "title": "Reported Article", "is_hidden": False}
    with patch("client.handlers.news_reporting_handler.get_json", side_effect=[fake_reports, fake_article]), \
         patch("builtins.input", side_effect=["1", "2", "b"]):
        handler.list_my_reported_articles()


def test_list_my_reported_articles_submenu_invalid_option(handler):
    fake_reports = [
        {"article_id": 10, "reason": "spam", "created_at": "2024-06-29T12:00:00"},
    ]
    fake_article = {"id": 10, "title": "Reported Article", "is_hidden": False}
    with patch(
        "client.handlers.news_reporting_handler.get_json",
        side_effect=[fake_reports, fake_article, fake_article, fake_article]
    ), patch(
        "builtins.input",
        side_effect=["1", "9", "9", "2", "b"]  # enough invalids, then go back, then exit
    ):
        handler.list_my_reported_articles()


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


def test_unreport_article_none_response(handler):
    with patch("client.handlers.news_reporting_handler.delete_json", return_value=None):
        handler.unreport_article(10)


def test_unreport_article_non_200_status(handler):
    class FakeResp:
        status_code = 500
    with patch("client.handlers.news_reporting_handler.delete_json", return_value=FakeResp()):
        handler.unreport_article(10)
