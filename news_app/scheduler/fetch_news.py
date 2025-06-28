import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from server.repository.db_connector import db
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.services.news_service import NewsService

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


def fetch_and_store_news():
    logging.info("Starting news fetch task...")

    connection = db.connect()
    if connection is None:
        logging.error("Database connection failed.")
        return

    try:
        article_repo = ArticleRepository(db)
        category_repo = CategoryRepository(db)
        source_repo = SourceRepository(db)
        viewed_repo = ViewedArticleRepository(db)
        likes_repo = LikesDislikesRepository(db)

        news_service = NewsService(
            article_repo, category_repo, source_repo, viewed_repo, likes_repo
        )

        news_service.fetch_and_store_news()
        connection.commit()
        logging.info("News fetched and stored successfully.")
    except Exception as e:
        connection.rollback()
        logging.error(f"Error during news fetching: {e}", exc_info=True)
    finally:
        db.close(connection)


if __name__ == "__main__":
    logging.info("Scheduler started for fetch_news.py")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        fetch_and_store_news, trigger="interval", hours=4, next_run_time=datetime.now()
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logging.warning("Scheduler stopped manually.")
