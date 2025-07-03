import pytest
from unittest.mock import patch
from client.handlers.news_source_handler import NewsSourceHandler


@pytest.fixture
def handler():
    return NewsSourceHandler(current_user={"id": 1})


def test_list_sources_with_data(handler):
    fake_sources = [
        {"id": 1, "name": "newsapi.org", "active": True},
        {"id": 2, "name": "thenewsapi.org", "active": False},
    ]
    with patch(
        "client.handlers.news_source_handler.get_json", return_value=fake_sources
    ):
        handler.list_sources()
        print("test_list_sources_with_data: sources =", fake_sources)


def test_list_sources_no_data(handler):
    with patch("client.handlers.news_source_handler.get_json", return_value=[]):
        handler.list_sources()
        print("test_list_sources_no_data: sources = []")


def test_add_source_success(handler):
    with patch(
        "client.handlers.news_source_handler.post_json",
        return_value=type("Resp", (), {"status_code": 201})(),
    ), patch("builtins.input", return_value="Reuters"):
        handler.add_source()
        print("test_add_source_success: status_code = 201")


def test_add_source_duplicate(handler):
    with patch(
        "client.handlers.news_source_handler.post_json",
        return_value=type("Resp", (), {"status_code": 409})(),
    ), patch("builtins.input", return_value="newsapi.org"):
        handler.add_source()
        print("test_add_source_duplicate: status_code = 409")


def test_add_source_empty_name(handler):
    with patch("builtins.input", return_value=""):
        handler.add_source()
        print("test_add_source_empty_name: input was empty")


def test_add_source_server_error(handler):
    with patch(
        "client.handlers.news_source_handler.post_json", return_value=None
    ), patch("builtins.input", return_value="Reuters"):
        handler.add_source()
        print("test_add_source_server_error: post_json returned None")


def test_remove_source_success(handler):
    with patch(
        "client.handlers.news_source_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 200})(),
    ), patch("builtins.input", return_value="1"):
        handler.remove_source()
        print("test_remove_source_success: status_code = 200")


def test_remove_source_invalid_id(handler):
    with patch("builtins.input", return_value="abc"):
        handler.remove_source()
        print("test_remove_source_invalid_id: input was 'abc'")


def test_remove_source_error(handler):
    with patch(
        "client.handlers.news_source_handler.delete_json",
        return_value=type("Resp", (), {"status_code": 500})(),
    ), patch("builtins.input", return_value="1"):
        handler.remove_source()
        print("test_remove_source_error: status_code = 500")


def test_manage_sources_list_option(handler):
    with patch("builtins.input", side_effect=["1", "4"]), \
         patch.object(handler, "list_sources") as mock_list:
        handler.manage_sources()
        mock_list.assert_called_once()


def test_manage_sources_add_option(handler):
    with patch("builtins.input", side_effect=["2", "4"]), \
         patch.object(handler, "add_source") as mock_add:
        handler.manage_sources()
        mock_add.assert_called_once()


def test_manage_sources_remove_option(handler):
    with patch("builtins.input", side_effect=["3", "4"]), \
         patch.object(handler, "remove_source") as mock_remove:
        handler.manage_sources()
        mock_remove.assert_called_once()


def test_manage_sources_invalid_option(handler):
    with patch("builtins.input", side_effect=["9", "4"]):
        handler.manage_sources()  # Should print 'Invalid choice.' and then exit


def test_add_source_unexpected_status(handler):
    class FakeResp:
        status_code = 500
    with patch("client.handlers.news_source_handler.post_json", return_value=FakeResp()), \
         patch("builtins.input", return_value="Reuters"):
        handler.add_source()


def test_remove_source_none_response(handler):
    with patch("client.handlers.news_source_handler.delete_json", return_value=None), \
         patch("builtins.input", return_value="1"):
        handler.remove_source()
