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
        resp = post_json(
            "/api/admin/keywords", {"keyword": keyword}, headers=self._headers()
        )
        if resp and resp.status_code == 201:
            print("Keyword added and blocked.")
        else:
            print("Failed to add keyword.")

    def unblock_keyword(self):
        keyword = input("Enter keyword to unblock: ").strip()
        if not keyword:
            print("Keyword required.")
            return
        resp = post_json(
            "/api/admin/unblock-keyword", {"keyword": keyword}, headers=self._headers()
        )
        if resp and resp.status_code == 200:
            print("Keyword unblocked.")
        else:
            print("Failed to unblock keyword.")

    def delete_keyword(self):
        keyword = input("Enter keyword to delete: ").strip()
        if not keyword:
            print("Keyword required.")
            return
        resp = post_json(
            "/api/admin/delete-keyword", {"keyword": keyword}, headers=self._headers()
        )
        if resp and resp.status_code == 200:
            print("Keyword deleted.")
        else:
            print("Failed to delete keyword.")
