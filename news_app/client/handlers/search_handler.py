import logging
from dateutil.parser import parse as parse_datetime
from client.utils.pagination_helper import cli_paginate_items
from client.utils.helpers import (
    get_json,
    print_article_row,
    print_article_details,
)


class SearchHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def search_articles(self):
        print("\n--- Search Articles ---")
        print("How would you like to search?")
        print("1. By keyword/category")
        print("2. By date range")

        choice = input("Enter choice (1/2): ").strip()

        keyword = category = ""
        start_date = end_date = None

        if choice == "1":
            keyword = input(
                "Enter keyword to search (leave blank to skip): "
            ).strip()
            category = input(
                "Enter category to filter (leave blank to skip): "
            ).strip()
            if not keyword and not category:
                print("Please enter at least a keyword or category.")
                logging.error(
                    "User %s tried to search articles without keyword or category.",
                    self.current_user["id"],
                )
                return

        elif choice == "2":
            start_date_str = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
            try:
                if start_date_str:
                    start_date = (
                        parse_datetime(start_date_str).date().isoformat()
                    )
                if end_date_str:
                    end_date = parse_datetime(end_date_str).date().isoformat()
            except Exception:
                print("Invalid date format. Please use YYYY-MM-DD.")
                logging.error(
                    "User %s entered invalid date format: start='%s', end='%s'",
                    self.current_user["id"],
                    start_date_str,
                    end_date_str,
                )
                return
            if not start_date and not end_date:
                print("Please enter at least a start or end date.")
                logging.error(
                    "User %s tried to search articles without start or end date.",
                    self.current_user["id"],
                )
                return
        else:
            print("Invalid choice.")
            logging.error(
                "User %s entered invalid search choice: %s",
                self.current_user["id"],
                choice,
            )
            return

        def fetch_fn(limit: int, offset: int):
            params = {"limit": limit, "offset": offset}
            if keyword:
                params["keyword"] = keyword
            if category:
                params["category"] = category
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            return get_json("/api/news/search", params=params, default=[])

        cli_paginate_items(
            fetch_fn=fetch_fn,
            title="Search Results",
            per_page=10,
            on_select=print_article_details,
            display_fn=print_article_row,
        )
