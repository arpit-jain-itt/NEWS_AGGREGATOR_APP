import logging
from client.utils.helpers import (
    get_json,
    post_json,
    delete_json,
    print_article_details,
)


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
            logging.error(
                "No reported articles found for user %s",
                self.current_user["id"],
            )
            return
        print("\n--- Reported Articles ---")
        for idx, item in enumerate(reported, 1):
            print(
                f"{idx}. Article ID: {item['article_id']} | Reports: {item['report_count']}"
            )
        choice = input(
            "\nEnter number to manage article or 'b' to go back: "
        ).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(reported)):
            print("Invalid choice.")
            logging.error(
                "Invalid reported article choice by user %s: %s",
                self.current_user["id"],
                choice,
            )
            return
        article_id = reported[int(choice) - 1]["article_id"]
        self.manage_reported_article(article_id)

    def manage_reported_article(self, article_id):
        article = get_json(
            f"/api/news/article/{article_id}",
            headers=self._headers(),
            default=None,
        )
        if not article:
            print("Failed to fetch article details.")
            logging.error(
                "Can't fetch details for reported article ID: %s by user %s",
                article_id,
                self.current_user["id"],
            )
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
                        f"/api/admin/hide-article/{article_id}",
                        headers=self._headers(),
                    )
                    if resp and resp.status_code == 200:
                        print("Article hidden (blocked).")
                        article["is_hidden"] = True
                    else:
                        print("Failed to hide article.")
                        logging.error(
                            "Can't hide reported article ID: %s by user %s",
                            article_id,
                            self.current_user["id"],
                        )
            elif choice == "3" and article.get("is_hidden"):
                resp = post_json(
                    f"/api/admin/unhide-article/{article_id}",
                    headers=self._headers(),
                )
                if resp and resp.status_code == 200:
                    print("Article unhidden (unblocked).")
                    article["is_hidden"] = False
                else:
                    print("Failed to unhide article.")
                    logging.error(
                        "Failed to unhide reported article ID: %s by user %s",
                        article_id,
                        self.current_user["id"],
                    )
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
            logging.error(
                "No blocked articles found for user %s",
                self.current_user["id"],
            )
            return
        print("\n--- Blocked Articles ---")
        for idx, item in enumerate(blocked, 1):
            print(f"{idx}. Article ID: {item['id']} | Title: {item['title']}")
        choice = input(
            "\nEnter number to manage article or 'b' to go back: "
        ).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(blocked)):
            print("Invalid choice.")
            logging.error(
                "Invalid blocked article choice by user %s: %s",
                self.current_user["id"],
                choice,
            )
            return
        article_id = blocked[int(choice) - 1]["id"]
        self.manage_blocked_article(article_id)

    def manage_blocked_article(self, article_id):
        article = get_json(
            f"/api/news/article/{article_id}",
            headers=self._headers(),
            default=None,
        )
        if not article:
            print("Failed to fetch article details.")
            logging.error(
                "Can't fetch details for blocked article ID: %s by user %s",
                article_id,
                self.current_user["id"],
            )
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
                        logging.error(
                            "Can't unhide blocked article ID: %s by user %s",
                            article_id,
                            self.current_user["id"],
                        )
            elif choice == "3":
                return
            else:
                print("Invalid choice.")

    def show_reported_article_details(self, article_id):
        article = get_json(
            f"/api/news/article/{article_id}",
            headers=self._headers(),
            default=None,
        )
        if not article:
            print("Failed to fetch article details.")
            logging.error(
                "Can't fetch details for reported article ID: %s by user %s",
                article_id,
                self.current_user["id"],
            )
            return
        print_article_details(article)

    def list_my_reported_articles(self):
        while True:
            reports = get_json(
                "/api/users/my-reports", headers=self._headers(), default=[]
            )
            if not reports:
                print("You have not reported any articles.")
                logging.error(
                    "No reported articles found for user %s",
                    self.current_user["id"],
                )
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
                logging.error(
                    "Invalid my-reported-article choice by user %s: %s",
                    self.current_user["id"],
                    choice,
                )
                continue
            article_id = reports[int(choice) - 1]["article_id"]

            while True:
                article = get_json(
                    f"/api/news/article/{article_id}",
                    headers=self._headers(),
                    default=None,
                )
                if not article:
                    print("Failed to fetch article details.")
                    logging.error(
                        "Failed to fetch details for my-reported article ID: %s by user %s",
                        article_id,
                        self.current_user["id"],
                    )
                    break
                print_article_details(article)
                print("\nOptions:")
                print("1. Unreport")
                print("2. Go Back")
                sub_choice = input("Choose an option: ").strip()
                if sub_choice == "1":
                    self.unreport_article(article_id)
                    break
                elif sub_choice == "2":
                    break
                else:
                    print("Invalid choice.")
            break

    def unreport_article(self, article_id):
        resp = delete_json(
            "/api/users/my-reports",
            payload={"article_id": article_id},
            headers=self._headers(),
        )
        if resp is None:
            print("Failed to connect to server.")
            logging.error(
                "Failed to connect to server when unreporting article ID: %s by user %s",
                article_id,
                self.current_user["id"],
            )
            return
        if resp.status_code == 200:
            print("Report removed successfully.")
        else:
            print("Failed to remove report.")
            logging.error(
                "Failed to remove report for article ID: %s by user %s. HTTP %s",
                article_id,
                self.current_user["id"],
                resp.status_code,
            )
