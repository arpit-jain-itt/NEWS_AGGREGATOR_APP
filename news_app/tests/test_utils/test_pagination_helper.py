import pytest
from client.utils import pagination_helper
from unittest.mock import patch, MagicMock

def test_cli_paginate_items_no_items():
    def fetch_fn(limit, offset):
        return []
    with patch("builtins.input", return_value="b"), patch("builtins.print") as mock_print:
        pagination_helper.cli_paginate_items(fetch_fn, title="Test")
        mock_print.assert_any_call("No items found.")


def test_cli_paginate_items_next_prev_back():
    items = [f"item{i}" for i in range(10)]
    def fetch_fn(limit, offset):
        return items[offset:offset+limit]
    with patch("builtins.input", side_effect=["n", "p", "b"]), patch("builtins.print"):
        pagination_helper.cli_paginate_items(fetch_fn, title="Test", per_page=5)


def test_cli_paginate_items_select_valid():
    items = [f"item{i}" for i in range(5)]
    called = {}
    def fetch_fn(limit, offset):
        return items[offset:offset+limit]
    def on_select(item):
        called["item"] = item
    with patch("builtins.input", side_effect=["3", "b"]), patch("builtins.print"):
        pagination_helper.cli_paginate_items(fetch_fn, title="Test", per_page=5, on_select=on_select)
    assert called["item"] == "item2"


def test_cli_paginate_items_select_invalid():
    items = [f"item{i}" for i in range(5)]
    def fetch_fn(limit, offset):
        return items[offset:offset+limit]
    with patch("builtins.input", side_effect=["10", "b"]), patch("builtins.print") as mock_print:
        pagination_helper.cli_paginate_items(fetch_fn, title="Test", per_page=5)
        mock_print.assert_any_call("Invalid item number.")


def test_cli_paginate_items_invalid_choice():
    items = [f"item{i}" for i in range(5)]
    def fetch_fn(limit, offset):
        return items[offset:offset+limit]
    with patch("builtins.input", side_effect=["x", "b"]), patch("builtins.print") as mock_print:
        pagination_helper.cli_paginate_items(fetch_fn, title="Test", per_page=5)
        mock_print.assert_any_call("Invalid choice.") 