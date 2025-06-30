import pytest
from unittest.mock import patch
from client.handlers.search_handler import SearchHandler


@pytest.fixture
def handler():
    return SearchHandler(current_user={"id": 1})


def test_search_by_keyword(handler):
    fake_articles = [{"id": 1, "title": "Search Result"}]
    with patch("builtins.input", side_effect=["1", "test", "", "b"]), patch(
        "client.handlers.search_handler.get_json", return_value=fake_articles
    ):
        handler.search_articles()
        print("test_search_by_keyword: articles =", fake_articles)


def test_search_by_category(handler):
    fake_articles = [{"id": 1, "title": "Category Result"}]
    with patch("builtins.input", side_effect=["1", "", "sports", "b"]), patch(
        "client.handlers.search_handler.get_json", return_value=fake_articles
    ):
        handler.search_articles()
        print("test_search_by_category: articles =", fake_articles)


def test_search_by_keyword_and_category(handler):
    fake_articles = [{"id": 1, "title": "Both Result"}]
    with patch("builtins.input", side_effect=["1", "test", "sports", "b"]), patch(
        "client.handlers.search_handler.get_json", return_value=fake_articles
    ):
        handler.search_articles()
        print("test_search_by_keyword_and_category: articles =", fake_articles)


def test_search_by_date_range(handler):
    fake_articles = [{"id": 1, "title": "Date Range Result"}]
    with patch(
        "builtins.input", side_effect=["2", "2024-06-01", "2024-06-30", "b"]
    ), patch("client.handlers.search_handler.get_json", return_value=fake_articles):
        handler.search_articles()
        print("test_search_by_date_range: articles =", fake_articles)


def test_search_by_date_range_invalid_date(handler):
    with patch("builtins.input", side_effect=["2", "invalid", ""]):
        handler.search_articles()
        print("test_search_by_date_range_invalid_date: input was invalid")


def test_search_by_date_range_no_dates(handler):
    with patch("builtins.input", side_effect=["2", "", ""]):
        handler.search_articles()
        print("test_search_by_date_range_no_dates: input was empty")


def test_search_invalid_choice(handler):
    with patch("builtins.input", side_effect=["3"]):
        handler.search_articles()
        print("test_search_invalid_choice: input was invalid")


def test_search_no_keyword_or_category(handler):
    with patch("builtins.input", side_effect=["1", "", ""]):
        handler.search_articles()
        print("test_search_no_keyword_or_category: input was empty")
