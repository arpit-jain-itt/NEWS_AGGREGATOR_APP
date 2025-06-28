from datetime import date, timedelta
from client.utils.pagination_helper import cli_paginate_items
from client.utils.helpers import (
    get_json,
    post_json,
    delete_json,
    print_article_row,
    print_article_details,
)


class NewsArticleHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

    def paginate_and_display(self, title, fetch_fn, on_select=None, display_fn=None):
        cli_paginate_items(
            fetch_fn=fetch_fn,
            title=title,
            per_page=5,
            on_select=on_select or self.view_article,
            display_fn=display_fn or print_article_row,
        )

    def view_article(self, article: dict):
        print_article_details(article)
        article_id = article.get("id")
        if not article_id:
            print("Missing article ID.")
            return
        self._article_action_menu(article_id)

    def _article_action_menu(self, article_id):
        print("\nOptions:\n1. Save Article\n2. Like\n3. Dislike\n4. Report\n5. Go Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self._save_article(article_id)
        elif choice == "2":
            self._react_to_article(article_id, True)
        elif choice == "3":
            self._react_to_article(article_id, False)
        elif choice == "4":
            self.report_article(article_id)
        elif choice == "5":
            return

    def _react_to_article(self, article_id: int, is_like: bool):
        resp = post_json(
            "/api/news/react",
            {
                "user_id": self.current_user["id"],
                "article_id": article_id,
                "is_like": is_like,
            },
            headers=self._headers(),
        )
        if resp is None:
            return
        if resp.status_code in (200, 201):
            try:
                msg = resp.json().get("data", {}).get("message", "")
                print(msg or "Action successful.")
            except Exception:
                print("Action successful.")
        else:
            print(f"Failed to react (HTTP {resp.status_code}).")

    def _save_article(self, article_id: int):
        resp = post_json(
            "/api/news/save",
            {"user_id": self.current_user["id"], "article_id": article_id},
            headers=self._headers(),
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
        resp = delete_json(route, headers=self._headers())
        if resp is None:
            return
        if resp.status_code == 200:
            print("Article removed from saved list.")
        elif resp.status_code == 404:
            print("Article not found in saved list.")
        else:
            print(f"Failed to remove article ({resp.status_code}).")

    def report_article(self, article_id: int):
        reason = input("Enter reason for reporting this article: ").strip()
        if not reason:
            print("Reason is required.")
            return
        resp = post_json(
            "/api/news/report",
            {
                "user_id": self.current_user["id"],
                "article_id": article_id,
                "reason": reason,
            },
            headers=self._headers(),
        )
        if resp is None:
            return
        if resp.status_code == 201:
            print("Report submitted.")
        elif resp.status_code == 500:
            print("Failed to submit report.")
        else:
            print(f"Failed to report article (HTTP {resp.status_code}).")

    def list_news(self):
        categories = get_json("/api/categories", headers=self._headers(), default=[])
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
            return get_json(
                "/api/news/latest",
                {"limit": limit, "offset": offset, "category": category},
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display(f"News in: {category or 'All'}", fetch)

    def list_saved_articles(self):
        def fetch(limit, offset):
            return get_json(
                "/api/news/saved",
                {
                    "user_id": self.current_user["id"],
                    "limit": limit,
                    "offset": offset,
                },
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display(
            "Saved Articles", fetch, on_select=self.view_saved_article
        )

    def view_saved_article(self, article: dict):
        print_article_details(article)
        article_id = article.get("id")
        if not article_id:
            print("Missing article ID.")
            return
        self._saved_article_action_menu(article_id)

    def _saved_article_action_menu(self, article_id):
        print("\nOptions:\n1. Remove from Saved\n2. Like\n3. Dislike\n4. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self._remove_saved_article(article_id)
        elif choice == "2":
            self._react_to_article(article_id, True)
        elif choice == "3":
            self._react_to_article(article_id, False)
        elif choice == "4":
            return

    def search_articles(self):
        keyword = input("Keyword (optional): ").strip()
        category = input("Category (optional): ").strip()
        if not keyword and not category:
            print("Provide at least one filter.")
            return

        def fetch(limit, offset):
            return get_json(
                "/api/news/search",
                {
                    "keyword": keyword,
                    "category": category,
                    "limit": limit,
                    "offset": offset,
                },
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display("Search Results", fetch)

    def view_headlines(self):
        start_date = (date.today() - timedelta(days=1)).isoformat()
        end_date = date.today().isoformat()

        def fetch(limit, offset):
            articles = get_json(
                "/api/news/headlines",
                {
                    "limit": limit,
                    "offset": offset,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                headers=self._headers(),
                default=[],
            )

            return articles

        self.paginate_and_display("Top Headlines", fetch)

    def list_liked_articles(self):
        def fetch(limit, offset):
            return get_json(
                "/api/news/reactions",
                {
                    "user_id": self.current_user["id"],
                    "type": "like",
                    "limit": limit,
                    "offset": offset,
                },
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display("Liked Articles", fetch, on_select=self.view_article)

    def list_disliked_articles(self):
        def fetch(limit, offset):
            return get_json(
                "/api/news/reactions",
                {
                    "user_id": self.current_user["id"],
                    "type": "dislike",
                    "limit": limit,
                    "offset": offset,
                },
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display(
            "Disliked Articles", fetch, on_select=self.view_article
        )

    # Personalized Articles
    def list_personalized_articles(self):
        """
        Fetch and display personalized articles for the current user.
        """

        def fetch(limit, offset):
            return get_json(
                f"/api/news/personalized/{self.current_user['id']}",
                {"limit": limit, "offset": offset},
                headers=self._headers(),
                default=[],
            )

        self.paginate_and_display("Personalized Articles", fetch)
