import pytest
from unittest.mock import patch, MagicMock
from client.utils import helpers
import requests


def test_extract_data_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": 123}
    assert helpers.extract_data(mock_resp) == 123


def test_extract_data_default():
    mock_resp = MagicMock()
    mock_resp.json.side_effect = Exception()
    assert helpers.extract_data(mock_resp, default="x") == "x"


def test_prompt_choice_valid():
    with patch("builtins.input", side_effect=["b"]):
        assert helpers.prompt_choice("?", ["a", "b"]) == "b"


def test_prompt_choice_invalid_then_valid():
    with patch("builtins.input", side_effect=["x", "b"]):
        assert helpers.prompt_choice("?", ["a", "b"]) == "b"


def test_prompt_yes_no_default_true():
    with patch("builtins.input", return_value=""):
        assert helpers.prompt_yes_no("?", default=True) is True


def test_prompt_yes_no_explicit_yes():
    with patch("builtins.input", return_value="y"):
        assert helpers.prompt_yes_no("?", default=False) is True


def test_prompt_yes_no_explicit_no():
    with patch("builtins.input", return_value="n"):
        assert helpers.prompt_yes_no("?", default=True) is False


def test_prompt_nonempty_valid():
    with patch("builtins.input", side_effect=["", "abc"]):
        assert helpers.prompt_nonempty("?") == "abc"


def test_prompt_int_valid():
    with patch("builtins.input", return_value="5"):
        assert helpers.prompt_int("?", min_value=1, max_value=10) == 5


def test_prompt_int_invalid_then_valid():
    with patch("builtins.input", side_effect=["x", "0", "11", "7"]):
        assert helpers.prompt_int("?", min_value=1, max_value=10) == 7


def test_menu_loop_back():
    options = {"1": ("Test", lambda: None)}
    with patch("builtins.input", side_effect=["b"]):
        helpers.menu_loop(options)


def test_menu_loop_valid_option():
    called = {}

    def fn():
        called["ok"] = True

    options = {"1": ("Test", fn)}
    with patch("builtins.input", side_effect=["1", "b"]):
        helpers.menu_loop(options)
    assert called["ok"] is True


def test_menu_loop_invalid_option():
    options = {"1": ("Test", lambda: None)}
    with patch("builtins.input", side_effect=["x", "b"]), patch(
        "builtins.print"
    ) as mock_print:
        helpers.menu_loop(options)
        mock_print.assert_any_call("Invalid choice.")


def test_get_json_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": 42}
    with patch("requests.get", return_value=mock_resp):
        assert helpers.get_json("/route") == 42


def test_get_json_connection_error():
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError()):
        assert helpers.get_json("/route", default="x") == "x"


def test_get_json_generic_exception():
    with patch("requests.get", side_effect=Exception()):
        assert helpers.get_json("/route", default="y") == "y"


def test_post_json_success():
    mock_resp = MagicMock()
    with patch("requests.post", return_value=mock_resp):
        assert helpers.post_json("/route", payload={}) == mock_resp


def test_post_json_connection_error():
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError()):
        assert helpers.post_json("/route") is None


def test_post_json_generic_exception():
    with patch("requests.post", side_effect=Exception()):
        assert helpers.post_json("/route") is None


def test_delete_json_success():
    mock_resp = MagicMock()
    with patch("requests.delete", return_value=mock_resp):
        assert helpers.delete_json("/route") == mock_resp
    with patch("requests.delete", return_value=mock_resp):
        assert helpers.delete_json("/route", payload={}) == mock_resp


def test_delete_json_connection_error():
    with patch("requests.delete", side_effect=requests.exceptions.ConnectionError()):
        assert helpers.delete_json("/route") is None


def test_delete_json_generic_exception():
    with patch("requests.delete", side_effect=Exception()):
        assert helpers.delete_json("/route") is None


def test_print_article_row():
    article = {"title": "T", "published_at": "2024-01-01"}
    with patch("builtins.print") as mock_print:
        helpers.print_article_row(article, 1)
        mock_print.assert_any_call("1. T (2024-01-01)")


def test_print_article_details():
    article = {
        "title": "T",
        "published_at": "2024-01-01",
        "description": "desc",
        "content": "c",
        "url": "u",
        "category_name": "cat",
    }
    with patch("builtins.print") as mock_print:
        helpers.print_article_details(article)
        mock_print.assert_any_call("Title: T")
        mock_print.assert_any_call("Published At: 2024-01-01")
        mock_print.assert_any_call("Description: desc")
        mock_print.assert_any_call("Content: c")
        mock_print.assert_any_call("URL: u")
        mock_print.assert_any_call("Category: cat")
