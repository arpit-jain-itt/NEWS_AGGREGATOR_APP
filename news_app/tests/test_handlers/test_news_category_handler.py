import pytest
from unittest.mock import patch
from client.handlers.news_category_handler import NewsCategoryHandler


@pytest.fixture
def handler():
    return NewsCategoryHandler(current_user={"id": 1})


def test_list_categories_with_data(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": False},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ):
        handler.list_categories()
        print("test_list_categories_with_data: categories =", fake_categories)


def test_list_categories_no_data(handler):
    with patch("client.handlers.news_category_handler.get_json", return_value=[]):
        handler.list_categories()
        print("test_list_categories_no_data: categories = []")


def test_add_category_success(handler):
    with patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 201})(),
    ), patch("builtins.input", return_value="tech"):
        handler.add_category()
        print("test_add_category_success: status_code = 201")


def test_add_category_duplicate(handler):
    with patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 409})(),
    ), patch("builtins.input", return_value="general"):
        handler.add_category()
        print("test_add_category_duplicate: status_code = 409")


def test_add_category_empty_name(handler):
    with patch("builtins.input", return_value=""):
        handler.add_category()
        print("test_add_category_empty_name: input was empty")


def test_add_category_server_error(handler):
    with patch(
        "client.handlers.news_category_handler.post_json", return_value=None
    ), patch("builtins.input", return_value="tech"):
        handler.add_category()
        print("test_add_category_server_error: post_json returned None")


def test_hide_category_success(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": False},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.hide_category()
        print("test_hide_category_success: status_code = 200")


def test_hide_category_invalid_id(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": False},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch("builtins.input", side_effect=["abc"]):
        handler.hide_category()
        print("test_hide_category_invalid_id: input was 'abc'")


def test_hide_category_error(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": False},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.hide_category()
        print("test_hide_category_error: status_code = 500")


def test_unhide_category_success(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": True},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.unhide_category()
        print("test_unhide_category_success: status_code = 200")


def test_unhide_category_invalid_id(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": True},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch("builtins.input", side_effect=["abc"]):
        handler.unhide_category()
        print("test_unhide_category_invalid_id: input was 'abc'")


def test_unhide_category_error(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": True},
        {"id": 2, "name": "sports", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.unhide_category()
        print("test_unhide_category_error: status_code = 500")


def test_manage_categories_list_option(handler):
    with patch("builtins.input", side_effect=["1", "5"]), patch.object(
        handler, "list_categories"
    ) as mock_list:
        handler.manage_categories()
        mock_list.assert_called_once()


def test_manage_categories_add_option(handler):
    with patch("builtins.input", side_effect=["2", "5"]), patch.object(
        handler, "add_category"
    ) as mock_add:
        handler.manage_categories()
        mock_add.assert_called_once()


def test_manage_categories_hide_option(handler):
    with patch("builtins.input", side_effect=["3", "5"]), patch.object(
        handler, "hide_category"
    ) as mock_hide:
        handler.manage_categories()
        mock_hide.assert_called_once()


def test_manage_categories_unhide_option(handler):
    with patch("builtins.input", side_effect=["4", "5"]), patch.object(
        handler, "unhide_category"
    ) as mock_unhide:
        handler.manage_categories()
        mock_unhide.assert_called_once()


def test_manage_categories_invalid_option(handler):
    with patch("builtins.input", side_effect=["9", "5"]):
        handler.manage_categories()


def test_add_category_unexpected_status(handler):
    class FakeResp:
        status_code = 500

    with patch(
        "client.handlers.news_category_handler.post_json", return_value=FakeResp()
    ), patch("builtins.input", return_value="newcat"):
        handler.add_category()


def test_hide_category_none_response(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": False},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json", return_value=None
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.hide_category()


def test_unhide_category_none_response(handler):
    fake_categories = [
        {"id": 1, "name": "general", "is_hidden": True},
    ]
    with patch(
        "client.handlers.news_category_handler.get_json", return_value=fake_categories
    ), patch(
        "client.handlers.news_category_handler.post_json", return_value=None
    ), patch(
        "builtins.input", side_effect=["1"]
    ):
        handler.unhide_category()


def test_list_categories_error_logging(handler):
    with patch(
        "client.handlers.news_category_handler.get_json", side_effect=Exception()
    ):
        with pytest.raises(Exception):
            handler.list_categories()
