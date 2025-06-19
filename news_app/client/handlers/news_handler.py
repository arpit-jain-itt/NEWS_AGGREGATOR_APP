import requests
from datetime import date, timedelta
from client.utils.pagination_helper import cli_paginate_items

SERVER_URL = "http://localhost:5000"


class NewsHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

    def _get_json(self, route: str, params=None, default=None):
        try:
            res = requests.get(
                f"{SERVER_URL}{route}", params=params, headers=self._headers()
            )
            return res.json().get("data", default)
        except Exception:
            print("GET failed or server unavailable.")
            return default

    def _post_json(self, route: str, payload=None):
        try:
            return requests.post(
                f"{SERVER_URL}{route}", json=payload, headers=self._headers()
            )
        except Exception:
            print("POST failed or server unavailable.")
            return None

    def _delete(self, route: str):
        try:
            return requests.delete(f"{SERVER_URL}{route}", headers=self._headers())
        except Exception:
            print("DELETE failed or server unavailable.")
            return None

    def _print_article_row(self, article: dict, idx: int):
        title = article.get("title", "[No Title]")
        pub = article.get("published_at", "N/A")
        print(f"{idx}. {title} ({pub})")

    def paginate_and_display(self, title, fetch_fn, on_select=None, display_fn=None):
        cli_paginate_items(
            fetch_fn=fetch_fn,
            title=title,
            per_page=5,
            on_select=on_select or self.view_article,
            display_fn=display_fn or self._print_article_row,
        )

    def view_article(self, article: dict):
        self._render_article(article)

        article_id = article.get("id")
        if not article_id:
            print("Missing article ID.")
            return

        self._post_json("/api/news/viewed", {"article_id": article_id})

        print("\nOptions:\n1. Save Article\n2. Like\n3. Dislike\n4. Go Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self._save_article(article_id)
        elif choice == "2":
            self._react_to_article(article_id, True)
        elif choice == "3":
            self._react_to_article(article_id, False)

    def view_saved_article(self, article: dict):
        self._render_article(article)

        article_id = article.get("id")
        if not article_id:
            print("Missing article ID.")
            return

        print("\nOptions:\n1. Remove from Saved\n2. Like\n3. Dislike\n4. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self._remove_saved_article(article_id)
        elif choice == "2":
            self._react_to_article(article_id, True)
        elif choice == "3":
            self._react_to_article(article_id, False)

    def _react_to_article(self, article_id: int, is_like: bool):
        resp = self._post_json(
            "/api/news/react",
            {
                "user_id": self.current_user["id"],
                "article_id": article_id,
                "is_like": is_like,
            },
        )
        if resp is None:
            return
        if resp.status_code in (200, 201):
            print("Article liked." if is_like else "Article disliked.")
        else:
            print(f"Failed to react (HTTP {resp.status_code}).")

    def _render_article(self, article: dict):
        print("\n--- Article Details ---")
        for label, key in [
            ("Title", "title"),
            ("Published At", "published_at"),
            ("Description", "description"),
            ("Content", "content"),
            ("URL", "url"),
            ("Category", "category_name"),
        ]:
            print(f"{label}: {article.get(key, 'N/A')}")

    def _save_article(self, article_id: int):
        resp = self._post_json(
            "/api/news/save",
            {"user_id": self.current_user["id"], "article_id": article_id},
        )
        if resp is None:
            return
        if resp.status_code in (200, 201):
            print("Article saved.")
        elif resp.status_code == 409:
            print("Article already saved.")
        else:
            print(f"Save failed ({resp.status_code}).")

    def _remove_saved_article(self, article_id: int):
        route = (
            f"/api/news/save?user_id={self.current_user['id']}&article_id={article_id}"
        )
        resp = self._delete(route)
        if resp is None:
            return
        if resp.status_code == 200:
            print("Article removed from saved list.")
        elif resp.status_code == 404:
            print("Article not found in saved list.")
        else:
            print(f"Failed to remove article ({resp.status_code}).")

    def list_news(self):
        categories = self._get_json("/api/categories", default=[])
        if not categories:
            print("No categories available.")
            return

        print("\n--- Categories ---\n0. All")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat['name']}")

        choice = input("Select category number: ").strip()
        if not choice.isdigit():
            print("Invalid input.")
            return
        idx = int(choice)
        if not 0 <= idx <= len(categories):
            print("Invalid category selection.")
            return

        category = "" if idx == 0 else categories[idx - 1]["name"]

        def fetch(limit, offset):
            return self._get_json(
                "/api/news/latest",
                {"limit": limit, "offset": offset, "category": category},
                default=[],
            )

        self.paginate_and_display(f"News in: {category or 'All'}", fetch)

    def list_saved_articles(self):
        def fetch(limit, offset):
            return self._get_json(
                "/api/news/saved",
                {
                    "user_id": self.current_user["id"],
                    "limit": limit,
                    "offset": offset,
                },
                default=[],
            )

        self.paginate_and_display(
            "Saved Articles", fetch, on_select=self.view_saved_article
        )

    def search_articles(self):
        keyword = input("Keyword (optional): ").strip()
        category = input("Category (optional): ").strip()
        if not keyword and not category:
            print("Provide at least one filter.")
            return

        def fetch(limit, offset):
            return self._get_json(
                "/api/news/search",
                {
                    "keyword": keyword,
                    "category": category,
                    "limit": limit,
                    "offset": offset,
                },
                default=[],
            )

        self.paginate_and_display("Search Results", fetch)

    def view_headlines(self):
        today = (date.today() - timedelta(days=2)).isoformat()

        def fetch(limit, offset):
            return self._get_json(
                "/api/news/headlines",
                {
                    "limit": limit,
                    "offset": offset,
                    "start_date": today,
                    "end_date": today,
                },
                default=[],
            )

        self.paginate_and_display("Top Headlines", fetch)

    def manage_sources(self):
        options = {
            "1": self._list_sources,
            "2": self._add_source,
            "3": self._remove_source,
        }
        while True:
            print("\n--- Manage Sources ---\n1. List\n2. Add\n3. Remove\n4. Back")
            choice = input("Select: ").strip()
            if choice == "4":
                break
            action = options.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    def _list_sources(self):
        sources = self._get_json("/api/admin/news-sources", default=[])
        for src in sources:
            status = "Active" if src.get("active") else "Inactive"
            print(f"{src['id']}: {src['name']} [{status}]")

    def _add_source(self):
        name = input("Source name: ").strip()
        if not name:
            print("Name required.")
            return
        resp = self._post_json("/api/admin/news-sources", {"name": name})
        if resp is None:
            return
        if resp.status_code == 201:
            print("Source added.")
        elif resp.status_code == 409:
            print("Source already exists.")
        else:
            print(f"Failed to add source (HTTP {resp.status_code}).")

    def _remove_source(self):
        src_id = input("Source ID to remove: ").strip()
        if not src_id.isdigit():
            print("Invalid ID.")
            return
        resp = self._delete(f"/api/admin/news-sources/{src_id}")
        if resp and resp.status_code == 200:
            print("Source removed.")
        else:
            print("Error removing source.")

    def manage_categories(self):
        options = {"1": self._add_category, "2": self._delete_category}
        while True:
            print("\n--- Manage Categories ---\n1. Add\n2. Delete\n3. Back")
            choice = input("Select: ").strip()
            if choice == "3":
                break
            action = options.get(choice)
            if action:
                action()
            else:
                print("Invalid option.")

    def _add_category(self):
        name = input("\nNew category name: ").strip()
        if not name:
            print("Name required.")
            return
        resp = self._post_json("/api/categories", {"name": name})
        if resp is None:
            return
        if resp.status_code == 201:
            print("Category added.")
        elif resp.status_code == 409:
            print("Category already exists.")
        else:
            print(f"Failed to add category (HTTP {resp.status_code}).")

    def _delete_category(self):
        categories = self._get_json("/api/categories", default=[])
        if not categories:
            print("No categories.")
            return
        for cat in categories:
            print(f"{cat['id']}: {cat['name']}")
        cat_id = input("\nCategory ID to delete: ").strip()
        if not cat_id.isdigit():
            print("Invalid ID.")
            return
        resp = self._delete(f"/api/categories/{cat_id}")
        if resp and resp.status_code == 200:
            print("Deleted.")
        else:
            print("Failed to delete.")

    def list_liked_articles(self):
        def fetch(limit, offset):
            return self._get_json(
                "/api/news/reactions",
                {
                    "user_id": self.current_user["id"],
                    "type": "like",
                    "limit": limit,
                    "offset": offset,
                },
                default=[],
            )

        self.paginate_and_display("Liked Articles", fetch, on_select=self.view_article)

    def list_disliked_articles(self):
        def fetch(limit, offset):
            return self._get_json(
                "/api/news/reactions",
                {
                    "user_id": self.current_user["id"],
                    "type": "dislike",
                    "limit": limit,
                    "offset": offset,
                },
                default=[],
            )

        self.paginate_and_display(
            "Disliked Articles", fetch, on_select=self.view_article
        )
