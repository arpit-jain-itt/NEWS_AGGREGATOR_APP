import logging
from client.utils.validators import validate_categories
from client.utils.helpers import get_json, post_json


class NotificationHandler:
    def __init__(self, current_user):
        self.current_user = current_user

    def manage_notifications(self):
        print("\n--- Notification Preferences ---")

        # Fetch existing prefs
        prefs = self._fetch_user_notification() or {}
        current_cats = ",".join(prefs.get("categories", []))
        current_keys = ",".join(prefs.get("keywords", []))
        email_on = prefs.get("notify_via_email", True)
        enabled = prefs.get("enabled", True)

        # Show current settings
        print(f"Current categories: {current_cats or '(none)'}")
        print(f"Current keywords:   {current_keys or '(none)'}")
        print(f"Notify via email:   {'Yes' if email_on else 'No'}")
        print(f"Notifications on:  {'Yes' if enabled else 'No'}\n")

        # Ask user what they want to do
        update_choice = (
            input("Do you want to update your notification preferences? (y/n): ")
            .strip()
            .lower()
        )
        if update_choice == "n":
            remove_choice = (
                input("Do you want to remove all notification preferences? (y/n): ")
                .strip()
                .lower()
            )
            if remove_choice == "y":
                payload = {
                    "user_id": self.current_user["id"],
                    "categories": "",
                    "keywords": "",
                    "notify_via_email": False,
                    "enabled": False,
                }
                resp = post_json("/api/notifications/preferences", payload=payload)
                if resp and resp.ok:
                    print("Notification preferences removed successfully.")
                else:
                    print("Failed to remove notification preferences.")
                    logging.error(
                        "Failed to remove notification preferences for user %s",
                        self.current_user["id"],
                    )
            else:
                print("No changes made to notification preferences.")
            return

        # Display category list
        all_categories = self._fetch_categories()
        valid_names = [cat["name"].lower() for cat in all_categories]
        if valid_names:
            print("Available categories:")
            print(", ".join(valid_names))
        else:
            print("(Could not fetch category list.)")
            logging.error(
                "Could not fetch category list for user %s",
                self.current_user["id"],
            )

        # Category input & validation
        cats_input_raw = input("Enter categories (comma separated): ").strip().lower()
        if cats_input_raw:
            is_valid, cleaned, invalid = validate_categories(
                cats_input_raw, valid_names
            )
            if not is_valid:
                print(f"Invalid categories: {', '.join(invalid)}")
                print("Please enter valid category names.")
                logging.error(
                    "User %s entered invalid categories: %s",
                    self.current_user["id"],
                    ", ".join(invalid),
                )
                return
            cats_input = ",".join(cleaned)
        else:
            cats_input = current_cats

        keys_input = input("Enter keywords   (comma separated): ").strip()
        email_input = input("Notify via email? (y/n): ").strip().lower()
        enabled_input = input("Enable notifications? (y/n): ").strip().lower()

        new_keys = keys_input or current_keys
        new_email_on = email_on if email_input == "" else email_input == "y"
        new_enabled = enabled if enabled_input == "" else enabled_input == "y"

        payload = {
            "user_id": self.current_user["id"],
            "categories": cats_input,
            "keywords": new_keys,
            "notify_via_email": new_email_on,
            "enabled": new_enabled,
        }

        resp = post_json("/api/notifications/preferences", payload=payload)
        if resp and resp.ok:
            print("Notification preferences updated successfully.")
        else:
            print("Failed to update notification preferences.")
            logging.error(
                "Failed to update notification preferences for user %s",
                self.current_user["id"],
            )

    def view_sent_notifications(self):
        print("\n--- Notification History ---")
        notifications = get_json(
            "/api/news/notifications/sent",
            params={"user_id": self.current_user["id"]},
            default=[],
        )
        if not notifications:
            print("No notifications have been sent to you yet.")
            return

        for idx, n in enumerate(notifications, 1):
            print(f"\n{idx}. {n.get('title', '(No Title)')}")
            print(f"   URL: {n.get('url', '-')}")
            print(f"   Description: {n.get('description', '-')}")
            print(f"   Published: {n.get('published_at', '-')}")
            print(f"   Notified (sent): {n.get('viewed_at', '-')}")
        print(f"\nTotal notifications sent: {len(notifications)}")

    def _fetch_user_notification(self):
        data = get_json(
            "/api/notifications/preferences",
            params={"user_id": self.current_user["id"]},
            default=None,
        )
        return data if data is not None else {}

    def _fetch_categories(self):
        return get_json("/api/categories", default=[])
