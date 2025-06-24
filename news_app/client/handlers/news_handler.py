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

    def _delete(self, route: str, payload=None):
        try:
            if payload:
                return requests.delete(
                    f"{SERVER_URL}{route}", json=payload, headers=self._headers()
                )
            else:
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
        self._article_action_menu(article_id)

    def view_saved_article(self, article: dict):
        self._render_article(article)
        article_id = article.get("id")
        if not article_id:
            print("Missing article ID.")
            return
        self._saved_article_action_menu(article_id)

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
            try:
                msg = resp.json().get("data", {}).get("message", "")
                print(msg or "Action successful.")
            except Exception:
                print("Action successful.")
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

    def report_article(self, article_id: int):
        reason = input("Enter reason for reporting this article: ").strip()
        if not reason:
            print("Reason is required.")
            return
        resp = self._post_json(
            "/api/news/report",
            {
                "user_id": self.current_user["id"],
                "article_id": article_id,
                "reason": reason,
            },
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

    def list_reported_articles(self):
        reported = self._get_json("/api/admin/reported-articles", default=[])
        if not reported:
            print("No reported articles.")
            return
        print("\n--- Reported Articles ---")
        for idx, item in enumerate(reported, 1):
            print(
                f"{idx}. Article ID: {item['article_id']} | Reports: {item['report_count']}"
            )
        choice = input("\nEnter number to manage article or 'b' to go back: ").strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(reported)):
            print("Invalid choice.")
            return
        article_id = reported[int(choice) - 1]["article_id"]
        self.manage_reported_article(article_id)

    def manage_reported_article(self, article_id):
        article = self._get_json(f"/api/news/article/{article_id}", default=None)
        if not article:
            print("Failed to fetch article details.")
            return

        while True:
            print(f"\nManaging Article ID: {article_id}")
            print("1. Show Details")
            print("2. Block (Hide) Article")
            if article.get("is_hidden"):
                print("3. Unblock (Unhide) Article")
            print("4. Go Back")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self._render_article(article)
            elif choice == "2":
                if article.get("is_hidden"):
                    print("Article is already hidden.")
                else:
                    resp = self._post_json(f"/api/admin/hide-article/{article_id}")
                    if resp and resp.status_code == 200:
                        print("Article hidden (blocked).")
                        article["is_hidden"] = True
                    else:
                        print("Failed to hide article.")
            elif choice == "3" and article.get("is_hidden"):
                resp = self._post_json(f"/api/admin/unhide-article/{article_id}")
                if resp and resp.status_code == 200:
                    print("Article unhidden (unblocked).")
                    article["is_hidden"] = False
                else:
                    print("Failed to unhide article.")
            elif choice == "4":
                return
            else:
                print("Invalid choice.")

    def list_blocked_articles(self):
        blocked = self._get_json("/api/admin/blocked-articles", default=[])
        if not blocked:
            print("No blocked articles.")
            return
        print("\n--- Blocked Articles ---")
        for idx, item in enumerate(blocked, 1):
            print(f"{idx}. Article ID: {item['id']} | Title: {item['title']}")
        choice = input("\nEnter number to manage article or 'b' to go back: ").strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(blocked)):
            print("Invalid choice.")
            return
        article_id = blocked[int(choice) - 1]["id"]
        self.manage_blocked_article(article_id)

    def manage_blocked_article(self, article_id):
        article = self._get_json(f"/api/news/article/{article_id}", default=None)
        if not article:
            print("Failed to fetch article details.")
            return

        while True:
            print(f"\nManaging Blocked Article ID: {article_id}")
            print("1. Show Details")
            print("2. Unblock (Unhide) Article")
            print("3. Go Back")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self._render_article(article)
            elif choice == "2":
                if not article.get("is_hidden"):
                    print("Article is already unhidden.")
                else:
                    resp = self._post_json(f"/api/admin/unhide-article/{article_id}")
                    if resp and resp.status_code == 200:
                        print("Article unhidden (unblocked).")
                        article["is_hidden"] = False
                    else:
                        print("Failed to unhide article.")
            elif choice == "3":
                return
            else:
                print("Invalid choice.")

    def show_reported_article_details(self, article_id):
        article = self._get_json(f"/api/news/article/{article_id}", default=None)
        if not article:
            print("Failed to fetch article details.")
            return
        self._render_article(article)
        input("\nPress Enter to go back...")

    def list_my_reported_articles(self):
        while True:
            reports = self._get_json("/api/users/my-reports", default=[])
            if not reports:
                print("You have not reported any articles.")
                return
            print("\n--- My Reported Articles ---")
            for idx, report in enumerate(reports, 1):
                print(
                    f"{idx}. Article ID: {report['article_id']} | Reason: {report.get('reason', '')} | Reported At: {report.get('created_at', '')}"
                )
            choice = input(
                "\nEnter number to view/unreport article or 'b' to go back: "
            ).strip()
            if choice.lower() == "b":
                return
            if not choice.isdigit() or not (1 <= int(choice) <= len(reports)):
                print("Invalid choice.")
                continue
            article_id = reports[int(choice) - 1]["article_id"]
            self.show_reported_article_details(article_id)
            unreport = (
                input("Do you want to unreport this article? (y/n): ").strip().lower()
            )
            if unreport == "y":
                self.unreport_article(article_id)
            break

    def unreport_article(self, article_id):
        resp = self._delete("/api/users/my-reports", payload={"article_id": article_id})
        if resp is None:
            print("Failed to connect to server.")
            return
        if resp.status_code == 200:
            print("Report removed successfully.")
        else:
            print("Failed to remove report.")

    def manage_keywords(self):
        while True:
            print("\n--- Manage Blocked Keywords ---")
            print("1. List Blocked Keywords")
            print("2. Add/Block Keyword")
            print("3. Unblock Keyword")
            print("4. Delete Keyword")
            print("5. Back")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.list_blocked_keywords()
            elif choice == "2":
                self.add_keyword()
            elif choice == "3":
                self.unblock_keyword()
            elif choice == "4":
                self.delete_keyword()
            elif choice == "5":
                return
            else:
                print("Invalid choice.")

    def list_blocked_keywords(self):
        keywords = self._get_json("/api/admin/keywords", default=[])
        if not keywords:
            print("No keywords in blocklist.")
            return
        print("\nBlocked Keywords:")
        for idx, k in enumerate(keywords, 1):
            status = "Active" if k.get("active") else "Inactive"
            print(f"{idx}. {k['keyword']} [{status}]")

    def add_keyword(self):
        keyword = input("Enter keyword to block: ").strip()
        if not keyword:
            print("Keyword required.")
            return
        resp = self._post_json("/api/admin/keywords", {"keyword": keyword})
        if resp and resp.status_code == 201:
            print("Keyword added and blocked.")
        else:
            print("Failed to add keyword.")

    def unblock_keyword(self):
        keyword = input("Enter keyword to unblock: ").strip()
        if not keyword:
            print("Keyword required.")
            return
        resp = self._post_json("/api/admin/unblock-keyword", {"keyword": keyword})
        if resp and resp.status_code == 200:
            print("Keyword unblocked.")
        else:
            print("Failed to unblock keyword.")

    def delete_keyword(self):
        keyword = input("Enter keyword to delete: ").strip()
        if not keyword:
            print("Keyword required.")
            return
        resp = self._post_json("/api/admin/delete-keyword", {"keyword": keyword})
        if resp and resp.status_code == 200:
            print("Keyword deleted.")
        else:
            print("Failed to delete keyword.")
