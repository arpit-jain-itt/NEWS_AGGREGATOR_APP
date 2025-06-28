import sys
import requests
from client.handlers.auth_handler import AuthHandler
from client.handlers.news_article_handler import NewsArticleHandler
from client.handlers.news_source_handler import NewsSourceHandler
from client.handlers.news_category_handler import NewsCategoryHandler
from client.handlers.news_reporting_handler import NewsReportingHandler
from client.handlers.news_keyword_handler import NewsKeywordHandler
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
    print("2. View Personalized Articles")
    print("3. View News by Category")
    print("4. Search Articles")
    print("5. View Saved Articles")
    print("6. View Liked Articles")
    print("7. View Disliked Articles")
    print("8. Notifications Settings")
    print("9. My Reported Articles")
    print("10. Logout")
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
    print("8. Manage Blocked Keywords")
    print("9. Logout")
    return input("Choose an option: ").strip()


def run():
    if not check_server():
        print(
            "Error: Server is not running. Please start the server before launching the client."
        )
        sys.exit(1)

    auth = AuthHandler()
    news_article = news_source = news_category = news_reporting = news_keyword = (
        notifications
    ) = search = None

    try:
        while True:
            if auth.current_user is None:
                choice = main_menu()
                if choice == "1":
                    user = auth.login()
                    if user:
                        news_article = NewsArticleHandler(user)
                        news_source = NewsSourceHandler(user)
                        news_category = NewsCategoryHandler(user)
                        news_reporting = NewsReportingHandler(user)
                        news_keyword = NewsKeywordHandler(user)
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
                        news_source.manage_sources()
                    elif choice == "3":
                        news_article.list_news()
                    elif choice == "4":
                        news_category.manage_categories()
                    elif choice == "5":
                        notifications.manage_notifications()
                    elif choice == "6":
                        news_reporting.list_reported_articles()
                    elif choice == "7":
                        news_reporting.list_blocked_articles()
                    elif choice == "8":
                        news_keyword.manage_keywords()
                    elif choice == "9":
                        auth.logout()
                        news_article = news_source = news_category = news_reporting = (
                            news_keyword
                        ) = notifications = search = None
                    else:
                        print("Invalid choice. Please try again.")
                # User Menu
                else:
                    choice = user_menu()
                    if choice == "1":
                        news_article.view_headlines()
                    elif choice == "2":
                        news_article.list_personalized_articles()
                    elif choice == "3":
                        try:
                            news_article.list_news()
                        except TypeError as e:
                            print(f"\nCategory error: {e}")
                        except Exception as e:
                            print(f"\nError while listing news: {e}")
                    elif choice == "4":
                        search.search_articles()
                    elif choice == "5":
                        news_article.list_saved_articles()
                    elif choice == "6":
                        news_article.list_liked_articles()
                    elif choice == "7":
                        news_article.list_disliked_articles()
                    elif choice == "8":
                        notifications.manage_notifications()
                    elif choice == "9":
                        news_reporting.list_my_reported_articles()
                    elif choice == "10":
                        auth.logout()
                        news_article = news_source = news_category = news_reporting = (
                            news_keyword
                        ) = notifications = search = None
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
