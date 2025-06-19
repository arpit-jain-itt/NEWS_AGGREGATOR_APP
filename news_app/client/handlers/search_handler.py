import requests
from dateutil.parser import parse as parse_datetime
from client.utils.pagination_helper import cli_paginate_items

SERVER_URL = "http://localhost:5000"


class SearchHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    @staticmethod
    def _extract_data(resp: requests.Response, default):
        try:
            return resp.json().get("data", default)
        except ValueError:
            return default

    def _get_json(self, route: str, params=None, default=None):
        try:
            resp = requests.get(f"{SERVER_URL}{route}", params=params or {})
            return self._extract_data(resp, default)
        except requests.exceptions.ConnectionError:
            print("Server is not running.")
            return default

    @staticmethod
    def _print_article_row(article: dict, idx: int):
        if not isinstance(article, dict):
            print(f"{idx}. [No data]")
            return
        title = article.get("title", "[No Title]")
        published = article.get("published_at", "N/A")
        print(f"{idx}. {title} ({published})")

    @staticmethod
    def _print_article_details(article: dict):
        print("\n--- Article Details ---")
        for label, field in (
            ("Title", "title"),
            ("Published At", "published_at"),
            ("Category", "category_name"),
            ("Description", "description"),
            ("Content", "content"),
            ("URL", "url"),
        ):
            print(f"{label}: {article.get(field, 'N/A')}")
        print()

    def search_articles(self):
        print("\n--- Search Articles ---")
        print("How would you like to search?")
        print("1. By keyword/category")
        print("2. By date range")

        choice = input("Enter choice (1/2): ").strip()

        keyword = category = ""
        start_date = end_date = None

        if choice == "1":
            keyword = input("Enter keyword to search (leave blank to skip): ").strip()
            category = input("Enter category to filter (leave blank to skip): ").strip()
            if not keyword and not category:
                print("Please enter at least a keyword or category.")
                return

        elif choice == "2":
            start_date_str = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
            try:
                if start_date_str:
                    start_date = parse_datetime(start_date_str).date().isoformat()
                if end_date_str:
                    end_date = parse_datetime(end_date_str).date().isoformat()
            except Exception:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
            if not start_date and not end_date:
                print("Please enter at least a start or end date.")
                return
        else:
            print("Invalid choice.")
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
            return self._get_json("/api/news/search", params=params, default=[])

        cli_paginate_items(
            fetch_fn=fetch_fn,
            title="Search Results",
            per_page=10,
            on_select=self._print_article_details,
            display_fn=self._print_article_row,
        )
