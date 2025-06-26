from client.utils.helpers import get_json, post_json, delete_json, print_article_details


class NewsReportingHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

    def list_reported_articles(self):
        reported = get_json(
            "/api/admin/reported-articles", headers=self._headers(), default=[]
        )
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
        article = get_json(
            f"/api/news/article/{article_id}", headers=self._headers(), default=None
        )
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
                print_article_details(article)
            elif choice == "2":
                if article.get("is_hidden"):
                    print("Article is already hidden.")
                else:
                    resp = post_json(
                        f"/api/admin/hide-article/{article_id}", headers=self._headers()
                    )
                    if resp and resp.status_code == 200:
                        print("Article hidden (blocked).")
                        article["is_hidden"] = True
                    else:
                        print("Failed to hide article.")
            elif choice == "3" and article.get("is_hidden"):
                resp = post_json(
                    f"/api/admin/unhide-article/{article_id}", headers=self._headers()
                )
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
        blocked = get_json(
            "/api/admin/blocked-articles", headers=self._headers(), default=[]
        )
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
        article = get_json(
            f"/api/news/article/{article_id}", headers=self._headers(), default=None
        )
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
                print_article_details(article)
            elif choice == "2":
                if not article.get("is_hidden"):
                    print("Article is already unhidden.")
                else:
                    resp = post_json(
                        f"/api/admin/unhide-article/{article_id}",
                        headers=self._headers(),
                    )
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
        article = get_json(
            f"/api/news/article/{article_id}", headers=self._headers(), default=None
        )
        if not article:
            print("Failed to fetch article details.")
            return
        print_article_details(article)
        input("\nPress Enter to go back...")

    def list_my_reported_articles(self):
        while True:
            reports = get_json(
                "/api/users/my-reports", headers=self._headers(), default=[]
            )
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
        resp = delete_json(
            "/api/users/my-reports",
            payload={"article_id": article_id},
            headers=self._headers(),
        )
        if resp is None:
            print("Failed to connect to server.")
            return
        if resp.status_code == 200:
            print("Report removed successfully.")
        else:
            print("Failed to remove report.")
