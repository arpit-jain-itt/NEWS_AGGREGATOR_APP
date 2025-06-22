import sys
import requests
from client.handlers.auth_handler import AuthHandler
from client.handlers.news_handler import NewsHandler
from client.handlers.notification_handler import NotificationHandler
from client.handlers.search_handler import SearchHandler


def check_server():
    try:
        return requests.get("http://localhost:5000/health").status_code == 200
    except requests.exceptions.RequestException:
        return False


def main_menu():
    print("\n--- News Aggregator CLI ---")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    return input("Choose an option: ").strip()


def user_menu():
    print("\n--- User Menu ---")
    print("1. View Headlines")
    print("2. View News by Category")
    print("3. Search Articles")
    print("4. View Saved Articles")
    print("5. View Liked Articles")
    print("6. View Disliked Articles")
    print("7. Notifications Settings")
    print("8. My Reported Articles")
    print("9. Logout")
    return input("Choose an option: ").strip()


def admin_menu():
    print("\n--- Admin Menu ---")
    print("1. Manage Users")
    print("2. Manage News Sources")
    print("3. View News")
    print("4. News Category Management")
    print("5. Notifications Settings")
    print("6. View Reported Articles")
    print("7. View Blocked Articles")
    print("8. Logout")
    return input("Choose an option: ").strip()


def run():
    if not check_server():
        print(
            "Error: Server is not running. Please start the server before launching the client."
        )
        sys.exit(1)

    auth = AuthHandler()
    news = notifications = search = None

    try:
        while True:
            if auth.current_user is None:
                choice = main_menu()
                if choice == "1":
                    user = auth.login()
                    if user:
                        news = NewsHandler(user)
                        notifications = NotificationHandler(user)
                        search = SearchHandler(user)
                elif choice == "2":
                    auth.register()
                elif choice == "3":
                    print("Exiting application. Goodbye!")
                    sys.exit(0)
                else:
                    print("Invalid choice. Please try again.")
            else:
                user = auth.current_user
                # Admin menu
                if user.get("is_admin"):
                    choice = admin_menu()
                    if choice == "1":
                        auth.manage_users()
                    elif choice == "2":
                        news.manage_sources()
                    elif choice == "3":
                        news.list_news()
                    elif choice == "4":
                        news.manage_categories()
                    elif choice == "5":
                        notifications.manage_notifications()
                    elif choice == "6":
                        news.list_reported_articles()
                    elif choice == "7":
                        news.list_blocked_articles()
                    elif choice == "8":
                        auth.logout()
                        news = notifications = search = None
                    else:
                        print("Invalid choice. Please try again.")
                # User Menu
                else:
                    choice = user_menu()
                    if choice == "1":
                        news.view_headlines()
                    elif choice == "2":
                        try:
                            news.list_news()
                        except TypeError as e:
                            print(f"\nCategory error: {e}")
                        except Exception as e:
                            print(f"\nError while listing news: {e}")
                    elif choice == "3":
                        search.search_articles()
                    elif choice == "4":
                        news.list_saved_articles()
                    elif choice == "5":
                        news.list_liked_articles()
                    elif choice == "6":
                        news.list_disliked_articles()
                    elif choice == "7":
                        notifications.manage_notifications()
                    elif choice == "8":
                        news.list_my_reported_articles()
                    elif choice == "9":
                        auth.logout()
                        news = notifications = search = None
                    else:
                        print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
