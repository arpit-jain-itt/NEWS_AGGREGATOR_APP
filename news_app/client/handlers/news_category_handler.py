from client.utils.helpers import get_json, post_json


class NewsCategoryHandler:
    def __init__(self, current_user: dict):
        self.current_user = current_user

    def _headers(self):
        return {"X-User-ID": str(self.current_user["id"])}

    def manage_categories(self):
        options = {
            "1": self.list_categories,
            "2": self.add_category,
            "3": self.hide_category,
            "4": self.unhide_category,
        }
        while True:
            print("\n--- Manage Categories ---")
            print("1. List")
            print("2. Add")
            print("3. Hide")
            print("4. Unhide")
            print("5. Back")
            choice = input("Select: ").strip()
            if choice == "5":
                break
            action = options.get(choice)
            if action:
                action()
            else:
                print("Invalid option.")

    def list_categories(self):
        categories = get_json(
            "/api/categories/admin/categories", headers=self._headers(), default=[]
        )
        if not categories:
            print("No categories.")
            return
        print("\nCategories:")
        for cat in categories:
            status = "Hidden" if cat.get("is_hidden") else "Visible"
            print(f"{cat['id']}: {cat['name']} [{status}]")

    def add_category(self):
        name = input("\nNew category name: ").strip()
        if not name:
            print("Name required.")
            return
        resp = post_json("/api/categories", {"name": name}, headers=self._headers())
        if resp is None:
            return
        if resp.status_code == 201:
            print("Category added.")
        elif resp.status_code == 409:
            print("Category already exists.")
        else:
            print(f"Failed to add category (HTTP {resp.status_code}).")

    def hide_category(self):
        self.list_categories()
        cat_id = input("\nCategory ID to hide: ").strip()
        if not cat_id.isdigit():
            print("Invalid ID.")
            return
        resp = post_json(f"/api/admin/hide-category/{cat_id}", headers=self._headers())
        if resp and resp.status_code == 200:
            print("Category hidden.")
        else:
            print("Failed to hide category.")

    def unhide_category(self):
        self.list_categories()
        cat_id = input("\nCategory ID to unhide: ").strip()
        if not cat_id.isdigit():
            print("Invalid ID.")
            return
        resp = post_json(
            f"/api/admin/unhide-category/{cat_id}", headers=self._headers()
        )
        if resp and resp.status_code == 200:
            print("Category unhidden.")
        else:
            print("Failed to unhide category.")
