import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from server.repository.notification_repository import NotificationRepository
from server.repository.user_repository import UserRepository
from server.repository.article_repository import ArticleRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.db_connector import db
from server.services.email_service import EmailService
from server.services.notification_service import NotificationService

os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/scheduler.log"
LOG_LEVEL = logging.WARNING

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
handler.setLevel(LOG_LEVEL)

logging.basicConfig(level=LOG_LEVEL, handlers=[handler])


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

    logging.info("Sending notification emails to users...")
    try:
        notification_service.send_notifications()
        logging.info("Notifications sent successfully.")
    except Exception as e:
        logging.error(f"Error sending notifications: {e}", exc_info=True)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(
        send_scheduled_notifications,
        "interval",
        hours=4,
        minutes=5,
        next_run_time=datetime.now() + timedelta(seconds=1),
    )
    logging.info("Scheduler started for email_scheduler.py")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Scheduler stopped by user.")
