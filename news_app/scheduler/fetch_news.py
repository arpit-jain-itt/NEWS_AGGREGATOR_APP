from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from server.repository.db_connector import db
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.services.news_service import NewsService


def fetch_and_store_news():
    print(f"[{datetime.now()}] Starting fetch_and_store_news task...")

    article_repo = ArticleRepository(db)
    category_repo = CategoryRepository(db)
    source_repo = SourceRepository(db)
    viewed_repo = ViewedArticleRepository(db)
    news_service = NewsService(article_repo, category_repo, source_repo, viewed_repo)

    try:
        news_service.fetch_and_store_news()
        print(f"[{datetime.now()}] News fetching completed.")
    except Exception as e:
        print(f"[{datetime.now()}] Error during fetch: {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        fetch_and_store_news, "interval", hours=4, next_run_time=datetime.now()
    )
    print(f"[{datetime.now()}] Scheduler started for fetch_news.py")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
