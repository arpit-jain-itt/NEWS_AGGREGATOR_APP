import logging
from client.utils.helpers import get_json, post_json


class NewsKeywordHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

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
        keywords = get_json("/api/admin/keywords", headers=self._headers(), default=[])
        if not keywords:
            print("No keywords in blocklist.")
            logging.error(
                "No blocked keywords found for user %s", self.current_user["id"]
            )
            return
        print("\nBlocked Keywords:")
        for idx, k in enumerate(keywords, 1):
            status = "Active" if k.get("active") else "Inactive"
            print(f"{idx}. {k['keyword']} [{status}]")

    def add_keyword(self):
        keyword = input("Enter keyword to block: ").strip()
        if not keyword:
            print("Keyword required.")
            logging.error(
                "User %s tried to add a blocked keyword with empty input.",
                self.current_user["id"],
            )
            return
        resp = post_json(
            "/api/admin/keywords", {"keyword": keyword}, headers=self._headers()
        )
        if not (resp and resp.status_code == 201):
            print("Failed to add keyword.")
            logging.error(
                "Failed to add blocked keyword '%s' by user %s.",
                keyword,
                self.current_user["id"],
            )
        else:
            print("Keyword added and blocked.")

    def unblock_keyword(self):
        keyword = input("Enter keyword to unblock: ").strip()
        if not keyword:
            print("Keyword required.")
            logging.error(
                "User %s tried to unblock a keyword with empty input.",
                self.current_user["id"],
            )
            return
        resp = post_json(
            "/api/admin/unblock-keyword", {"keyword": keyword}, headers=self._headers()
        )
        if not (resp and resp.status_code == 200):
            print("Failed to unblock keyword.")
            logging.error(
                "Failed to unblock keyword '%s' by user %s.",
                keyword,
                self.current_user["id"],
            )
        else:
            print("Keyword unblocked.")

    def delete_keyword(self):
        keyword = input("Enter keyword to delete: ").strip()
        if not keyword:
            print("Keyword required.")
            logging.error(
                "User %s tried to delete a keyword with empty input.",
                self.current_user["id"],
            )
            return
        resp = post_json(
            "/api/admin/delete-keyword", {"keyword": keyword}, headers=self._headers()
        )
        if not (resp and resp.status_code == 200):
            print("Failed to delete keyword.")
            logging.error(
                "Failed to delete keyword '%s' by user %s.",
                keyword,
                self.current_user["id"],
            )
        else:
            print("Keyword deleted.")
