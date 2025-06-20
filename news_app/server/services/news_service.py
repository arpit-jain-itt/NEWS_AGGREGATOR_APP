from typing import List, Optional, Literal
from datetime import datetime
from dateutil.parser import parse as parse_datetime

from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.external_apis.newsapi_org import NewsApiOrgClient
from server.external_apis.thenewsapi_com import TheNewsApiClient
from server.models.article_model import Article


class NewsService:

    MAX_ARTICLES = 6

    def __init__(
        self,
        article_repo: ArticleRepository,
        category_repo: CategoryRepository,
        source_repo: SourceRepository,
        viewed_repo: ViewedArticleRepository,
        likes_repo: LikesDislikesRepository,
    ):
        self.article_repo = article_repo
        self.category_repo = category_repo
        self.source_repo = source_repo
        self.viewed_repo = viewed_repo
        self.likes_repo = likes_repo

    def fetch_and_store_news(self) -> None:
        # first go for newsapi, then thenewsapi
        all_sources = self.source_repo.get_all_sources()
        primary_source = next((s for s in all_sources if s.name == "News API"), None)
        secondary_source = next(
            (s for s in all_sources if s.name == "The News API"), None
        )

        if not primary_source:
            print("No 'News API' source configured.")
            return

        categories = [c.name for c in self.category_repo.get_all_categories()]
        total_inserted = 0

        total_inserted += self._insert_from_provider(
            client=NewsApiOrgClient(),
            source=primary_source,
            categories=categories,
            already_inserted=total_inserted,
        )

        if total_inserted < self.MAX_ARTICLES and secondary_source:
            total_inserted += self._insert_from_provider(
                client=TheNewsApiClient(),
                source=secondary_source,
                categories=categories,
                already_inserted=total_inserted,
            )

        if total_inserted:
            src_id = (
                secondary_source.id
                if total_inserted < self.MAX_ARTICLES and secondary_source
                else primary_source.id
            )
            self.source_repo.update_last_accessed(src_id, datetime.now())

    def _insert_from_provider(
        self,
        client,
        source,
        categories: List[str],
        already_inserted: int,
    ) -> int:
        inserted = 0
        remaining = self.MAX_ARTICLES - already_inserted

        for category in categories:
            if inserted >= remaining:
                break

            try:
                headlines = client.fetch_top_headlines(category)
            except Exception as err:
                print(f"[NewsService] {source.name} error: {err}")
                continue

            for article in headlines:
                if inserted >= remaining:
                    break

                published_at = self._parse_ts(
                    article.get("publishedAt")
                    or article.get("published_at")
                    or article.get("date")
                )

                self.article_repo.insert_article(
                    title=article.get("title"),
                    description=article.get("description"),
                    url=article.get("url"),
                    published_at=published_at,
                    source_id=source.id,
                    category_id=self._category_id(category),
                    content=article.get("content") or article.get("snippet"),
                )
                inserted += 1

        return inserted

    @staticmethod
    def _parse_ts(raw: Optional[str]) -> datetime:
        try:
            return parse_datetime(raw) if raw else datetime.now()
        except Exception:
            return datetime.now()

    def _category_id(self, category_name: str) -> int:
        cat = self.category_repo.get_category_by_name(category_name)
        if cat:
            return cat.id
        # go to general category if not match with any other ones
        return self.category_repo.get_general_category().id

    def get_latest_articles(
        self,
        category_name: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        cat_id = None
        if category_name:
            cat = self.category_repo.get_category_by_name(category_name)
            if not cat:
                return []
            cat_id = cat.id
        return self.article_repo.search_articles(
            keyword="",
            category_id=cat_id,
            start_date=None,
            end_date=None,
            limit=limit,
            offset=offset,
        )

    def search_articles(
        self,
        keyword: str = "",
        category: str = "",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        keyword = keyword.strip().lower()
        cat_id = None
        if category:
            cat = self.category_repo.get_category_by_name(category.strip())
            if not cat:
                return []
            cat_id = cat.id
        return self.article_repo.search_articles(
            keyword=keyword,
            category_id=cat_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    def mark_article_viewed(self, user_id: int, article_id: int) -> None:
        self.viewed_repo.mark_viewed(user_id, article_id)

    def save_article(self, user_id: int, article_id: int) -> str:
        return self.article_repo.save_article_for_user(user_id, article_id)

    def remove_saved_article(self, user_id: int, article_id: int) -> str:
        return self.article_repo.remove_saved_article(user_id, article_id)

    def get_saved_articles_by_user(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> List[Article]:
        return self.article_repo.get_saved_articles_by_user(
            user_id, limit=limit, offset=offset
        )

    def react_to_article(self, user_id: int, article_id: int, is_like: bool) -> str:
        return self.likes_repo.upsert_reaction(user_id, article_id, is_like)

    def remove_reaction(self, user_id: int, article_id: int) -> str:
        return self.likes_repo.delete_reaction(user_id, article_id)

    def get_reaction_summary(self, user_id: int) -> dict:
        likes, dislikes = self.likes_repo.get_reaction_summary(user_id)
        return {"likes": likes, "dislikes": dislikes}

    def get_reacted_articles(
        self,
        user_id: int,
        reaction_type: Literal["like", "dislike"],
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        is_like = reaction_type == "like"
        return self.likes_repo.get_reacted_articles(
            user_id=user_id,
            is_like=is_like,
            limit=limit,
            offset=offset,
        )
