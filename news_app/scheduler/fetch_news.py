from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from server.repository.db_connector import db
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.services.news_service import NewsService


def fetch_and_store_news():
    print(f"[{datetime.now()}] Starting news fetch task...")

    connection = db.connect()
    if connection is None:
        print(f"[{datetime.now()}] Database connection failed.")
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
        print(f"[{datetime.now()}] News fetched and stored successfully.")
    except Exception as e:
        connection.rollback()
        print(f"[{datetime.now()}] Error during news fetching: {e}")
    finally:
        db.close(connection)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Scheduler started for fetch_news.py")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        fetch_and_store_news, trigger="interval", hours=4, next_run_time=datetime.now()
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] Scheduler stopped manually.")
