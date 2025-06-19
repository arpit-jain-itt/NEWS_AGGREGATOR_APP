from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from server.repository.notification_repository import NotificationRepository
from server.repository.user_repository import UserRepository
from server.repository.article_repository import ArticleRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.db_connector import db
from server.services.email_service import EmailService
from server.services.notification_service import NotificationService


def send_scheduled_notifications():
    notification_repo = NotificationRepository(db)
    user_repo = UserRepository(db)
    article_repo = ArticleRepository(db)
    viewed_repo = ViewedArticleRepository(db)
    email_service = EmailService()

    notification_service = NotificationService(
        notification_repo,
        user_repo,
        article_repo,
        viewed_repo,
        email_service,
    )

    print(f"[{datetime.now()}] Sending notification emails to users...")
    try:
        notification_service.send_notifications()
        print(f"[{datetime.now()}] Notifications sent successfully.")
    except Exception as e:
        print(f"[{datetime.now()}] Error sending notifications: {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(
        send_scheduled_notifications,
        "interval",
        hours=4,
        minutes=5,
        next_run_time=datetime.now() + timedelta(seconds=1),
    )
    print(f"[{datetime.now()}] Scheduler started for email_scheduler.py")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
