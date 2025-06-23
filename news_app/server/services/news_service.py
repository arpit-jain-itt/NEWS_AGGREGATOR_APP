from typing import List, Optional, Literal
from datetime import datetime
from dateutil.parser import parse as parse_datetime
from server.models.report_model import Report
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.repository.keyword_filter_repository import KeywordFilterRepository
from server.repository.report_repository import ReportRepository
from server.models.article_model import Article
from server.external_apis.newsapi_org import NewsApiOrgClient
from server.external_apis.thenewsapi_com import TheNewsApiClient
from config.config import REPORT_THRESHOLD


class NewsService:

    MAX_ARTICLES = 6

    def __init__(
        self,
        article_repo: ArticleRepository,
        category_repo: CategoryRepository,
        source_repo: SourceRepository,
        viewed_repo: ViewedArticleRepository,
        likes_repo: LikesDislikesRepository,
        keyword_repo: Optional[KeywordFilterRepository] = None,
        report_repo: Optional[ReportRepository] = None,
    ):
        self.article_repo = article_repo
        self.category_repo = category_repo
        self.source_repo = source_repo
        self.viewed_repo = viewed_repo
        self.likes_repo = likes_repo
        self.keyword_repo = keyword_repo
        self.report_repo = report_repo

    def fetch_and_store_news(self) -> None:
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
            total_to_fetch=self.MAX_ARTICLES,
        )

        if total_inserted < self.MAX_ARTICLES and secondary_source:
            total_inserted += self._insert_from_provider(
                client=TheNewsApiClient(),
                source=secondary_source,
                categories=categories,
                total_to_fetch=self.MAX_ARTICLES - total_inserted,
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
        total_to_fetch: int,
    ) -> int:
        inserted = 0

        for category in categories:
            if inserted >= total_to_fetch:
                break

            try:
                headlines = client.fetch_top_headlines(category)
            except Exception:
                continue

            for article in headlines:
                if inserted >= total_to_fetch:
                    break

                published_at = self._parse_ts(
                    article.get("publishedAt")
                    or article.get("published_at")
                    or article.get("date")
                )

                if self.keyword_repo:
                    blocked_keywords = [
                        k.keyword for k in self.keyword_repo.get_all_keywords()
                    ]
                    if any(
                        bk.lower() in (article.get("title") or "").lower()
                        for bk in blocked_keywords
                    ):
                        continue

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
                break

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
            if not cat or cat.is_hidden:
                return []
            cat_id = cat.id
        return self.article_repo.search_articles(
            keyword="",
            category_id=cat_id,
            start_date=None,
            end_date=None,
            limit=limit,
            offset=offset,
            include_hidden=False,
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
            if not cat or cat.is_hidden:
                return []
            cat_id = cat.id

        if self.keyword_repo:
            blocked_keywords = [k.keyword for k in self.keyword_repo.get_all_keywords()]
            if any(bk in keyword for bk in blocked_keywords):
                return []
        return self.article_repo.search_articles(
            keyword=keyword,
            category_id=cat_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            include_hidden=False,
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
            user_id, limit=limit, offset=offset, include_hidden=False
        )

    def react_to_article(self, user_id: int, article_id: int, is_like: bool) -> str:
        current = self.likes_repo.get_user_reaction(user_id, article_id)
        if current is None:
            return self.likes_repo.upsert_reaction(user_id, article_id, is_like)
        if current == is_like:
            return self._delete_reaction_and_return(user_id, article_id)
        return self._delete_reaction_and_return(user_id, article_id)

    def _delete_reaction_and_return(self, user_id: int, article_id: int) -> str:
        status = self.likes_repo.delete_reaction(user_id, article_id)
        return "deleted" if status in ("deleted", "not_found") else status

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

    def report_article(self, user_id: int, article_id: int, reason: str) -> bool:
        report = Report(
            id=None,
            user_id=user_id,
            article_id=article_id,
            reason=reason,
            created_at=None,
            status="pending",
        )
        success = self.report_repo.add_report(report)
        if not success:
            return False
        count = self.report_repo.get_report_count(article_id)
        if count >= REPORT_THRESHOLD:
            self.article_repo.set_article_hidden(article_id, True)
            self.report_repo.update_report_status(article_id, "auto-blocked")
        return True

    def get_article_reactions_count(self, article_id: int) -> dict:
        return self.likes_repo.get_article_reactions_count(article_id)
