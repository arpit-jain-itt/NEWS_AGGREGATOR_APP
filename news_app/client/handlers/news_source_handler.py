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
            return
        print("\n--- News Sources ---")
        for src in sources:
            status = "Active" if src.get("active") else "Inactive"
            print(f"{src['id']}: {src['name']} [{status}]")

    def add_source(self):
        name = input("Source name: ").strip()
        if not name:
            print("Name required.")
            return
        resp = post_json(
            "/api/admin/news-sources", {"name": name}, headers=self._headers()
        )
        if resp is None:
            return
        if resp.status_code == 201:
            print("Source added.")
        elif resp.status_code == 409:
            print("Source already exists.")
        else:
            print(f"Failed to add source (HTTP {resp.status_code}).")

    def remove_source(self):
        src_id = input("Source ID to remove: ").strip()
        if not src_id.isdigit():
            print("Invalid ID.")
            return
        resp = delete_json(f"/api/admin/news-sources/{src_id}", headers=self._headers())
        if resp and resp.status_code == 200:
            print("Source removed.")
        else:
            print("Error removing source.")
