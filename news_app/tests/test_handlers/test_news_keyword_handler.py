import pytest
from unittest.mock import patch
from client.handlers.news_keyword_handler import NewsKeywordHandler


@pytest.fixture
def handler():
    return NewsKeywordHandler(current_user={"id": 1})


def test_list_blocked_keywords_with_data(handler):
    fake_keywords = [
        {"keyword": "spam", "active": True},
        {"keyword": "ads", "active": False},
    ]
    with patch(
        "client.handlers.news_keyword_handler.get_json", return_value=fake_keywords
    ):
        handler.list_blocked_keywords()
        print("test_list_blocked_keywords_with_data: keywords =", fake_keywords)


def test_list_blocked_keywords_no_data(handler):
    with patch("client.handlers.news_keyword_handler.get_json", return_value=[]):
        handler.list_blocked_keywords()
        print("test_list_blocked_keywords_no_data: keywords = []")


def test_add_keyword_success(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 201})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.add_keyword()
        print("test_add_keyword_success: status_code = 201")


def test_add_keyword_empty(handler):
    with patch("builtins.input", return_value=""):
        handler.add_keyword()
        print("test_add_keyword_empty: input was empty")


def test_add_keyword_error(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.add_keyword()
        print("test_add_keyword_error: status_code = 500")


def test_unblock_keyword_success(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.unblock_keyword()
        print("test_unblock_keyword_success: status_code = 200")


def test_unblock_keyword_empty(handler):
    with patch("builtins.input", return_value=""):
        handler.unblock_keyword()
        print("test_unblock_keyword_empty: input was empty")


def test_unblock_keyword_error(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.unblock_keyword()
        print("test_unblock_keyword_error: status_code = 500")


def test_delete_keyword_success(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.delete_keyword()
        print("test_delete_keyword_success: status_code = 200")


def test_delete_keyword_empty(handler):
    with patch("builtins.input", return_value=""):
        handler.delete_keyword()
        print("test_delete_keyword_empty: input was empty")


def test_delete_keyword_error(handler):
    with patch(
        "client.handlers.news_keyword_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch("builtins.input", return_value="blockme"):
        handler.delete_keyword()
        print("test_delete_keyword_error: status_code = 500")
