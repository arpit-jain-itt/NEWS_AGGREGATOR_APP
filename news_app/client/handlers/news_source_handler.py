import logging
from client.utils.helpers import get_json, post_json, delete_json


class NewsSourceHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

    def manage_sources(self):
        options = {
            "1": self.list_sources,
            "2": self.add_source,
            "3": self.remove_source,
        }
        while True:
            print("\n--- Manage Sources ---")
            print("1. List")
            print("2. Add")
            print("3. Remove")
            print("4. Back")
            choice = input("Select: ").strip()
            if choice == "4":
                break
            action = options.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    def list_sources(self):
        sources = get_json(
            "/api/admin/news-sources", headers=self._headers(), default=[]
        )
        if not sources:
            print("No sources found.")
            logging.error(
                "No news sources found for user %s", self.current_user["id"]
            )
            return
        print("\n--- News Sources ---")
        for src in sources:
            status = "Active" if src.get("active") else "Inactive"
            print(f"{src['id']}: {src['name']} [{status}]")

    def add_source(self):
        name = input("Source name: ").strip()
        if not name:
            print("Name required.")
            logging.error(
                "User %s tried to add a news source with empty name.",
                self.current_user["id"],
            )
            return
        resp = post_json(
            "/api/admin/news-sources", {"name": name}, headers=self._headers()
        )
        if resp is None:
            logging.error(
                "No response from server when adding news source '%s' by user %s.",
                name,
                self.current_user["id"],
            )
            return
        if resp.status_code == 201:
            print("Source added.")
        elif resp.status_code == 409:
            print("Source already exists.")
        else:
            print(f"Failed to add source (HTTP {resp.status_code}).")
            logging.error(
                "Failed to add news source '%s' by user %s. HTTP %s",
                name,
                self.current_user["id"],
                resp.status_code,
            )

    def remove_source(self):
        src_id = input("Source ID to remove: ").strip()
        if not src_id.isdigit():
            print("Invalid ID.")
            logging.error(
                "User %s tried to remove news source with invalid ID: %s",
                self.current_user["id"],
                src_id,
            )
            return
        resp = delete_json(
            f"/api/admin/news-sources/{src_id}", headers=self._headers()
        )
        if not (resp and resp.status_code == 200):
            print("Error removing source.")
            logging.error(
                "Failed to remove news source ID: %s by user %s",
                src_id,
                self.current_user["id"],
            )
        else:
            print("Source removed.")
