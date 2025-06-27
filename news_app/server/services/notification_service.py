from typing import List, Optional
from server.repository.notification_repository import NotificationRepository
from server.repository.user_repository import UserRepository
from server.repository.article_repository import ArticleRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.services.email_service import EmailService
from server.models.notification_model import UserNotification
from server.models.article_model import Article
from server.utils.notification_pref_codec import decode_preferences
from server.utils.service_helper import (
    filter_by_categories,
    filter_by_keywords,
    compose_email_body,
    get_current_utc_time,
    handle_db_exception,
)


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        user_repo: UserRepository,
        article_repo: ArticleRepository,
        viewed_repo: ViewedArticleRepository,
        email_service: EmailService,
    ):
        self.notification_repo = notification_repo
        self.user_repo = user_repo
        self.article_repo = article_repo
        self.viewed_repo = viewed_repo
        self.email_service = email_service

    def send_notifications(self):
        notifications: List[UserNotification] = (
            self.notification_repo.get_all_enabled_notifications()
        )

        for notif in notifications:
            user = self.user_repo.get_user_by_id(notif.user_id)
            if not user:
                continue

            # Preferences
            pref = decode_preferences(notif.keywords)
            categories = [c.lower() for c in pref["categories"]]
            keywords = [kw.lower() for kw in pref["keywords"]]
            if not categories:
                continue

            # Already viewed
            viewed_article_ids = set(
                self.viewed_repo.get_viewed_article_ids_by_user(user.id)
            )

            # Fetch latest articles
            recent_articles = self.article_repo.search_articles(limit=100)

            # Category filter
            recent_articles = filter_by_categories(recent_articles, categories)

            # Keyword filter
            if keywords:
                recent_articles = filter_by_keywords(recent_articles, keywords)

            # Exclude already viewed
            matched_articles = [
                art for art in recent_articles if art.id not in viewed_article_ids
            ]

            # Send email
            if matched_articles and notif.notify_via_email:
                email_body = compose_email_body(user.username, matched_articles)
                self.email_service.send_email(
                    user.email, "Your News Alerts", email_body
                )
                self.notification_repo.mark_articles_as_viewed(
                    user.id, [a.id for a in matched_articles]
                )
                self.notification_repo.set_last_notification_time(
                    user.id, get_current_utc_time()
                )

    def get_user_notification(self, user_id: int) -> Optional[UserNotification]:
        return self.notification_repo.get_notification_by_user_id(user_id)

    def update_user_notification(
        self, notification_id: int, keywords: str, notify_via_email: bool, enabled: bool
    ) -> bool:
        def do_update():
            conn = self.notification_repo.db.connect()
            cursor = conn.cursor()
            query = """
                UPDATE user_notifications
                SET keywords = %s,
                    notify_via_email = %s,
                    enabled = %s,
                    last_notification_time = NULL
                WHERE id = %s
            """
            cursor.execute(
                query, (keywords, notify_via_email, enabled, notification_id)
            )
            conn.commit()
            cursor.close()

        return handle_db_exception(do_update)

    def create_user_notification(
        self, user_id: int, keywords: str, notify_via_email: bool, enabled: bool
    ) -> bool:
        def do_create():
            self.notification_repo.create_or_update_notification(
                user_id, keywords, notify_via_email, enabled
            )

        return handle_db_exception(do_create)
