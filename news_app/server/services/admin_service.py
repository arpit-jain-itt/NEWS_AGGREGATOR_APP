from typing import List, Optional
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.report_repository import ReportRepository
from server.repository.keyword_filter_repository import KeywordFilterRepository
from server.models.report_model import Report
from server.models.keyword_filter_model import KeywordFilter
from server.utils.service_helper import safe_repo_call


class AdminService:
    def __init__(
        self,
        article_repo: ArticleRepository,
        category_repo: CategoryRepository,
        report_repo: ReportRepository,
        keyword_repo: KeywordFilterRepository,
    ):
        self.article_repo = article_repo
        self.category_repo = category_repo
        self.report_repo = report_repo
        self.keyword_repo = keyword_repo

    def get_reported_articles(self) -> List[dict]:
        return safe_repo_call(
            self.report_repo, "get_reported_articles", default=[]
        )

    def get_reports_for_article(self, article_id: int) -> List[Report]:
        return safe_repo_call(
            self.report_repo, "get_reports_for_article", article_id, default=[]
        )

    def hide_article(self, article_id: int) -> bool:
        return safe_repo_call(
            self.article_repo,
            "set_article_hidden",
            article_id,
            True,
            default=False,
        )

    def unhide_article(self, article_id: int) -> bool:
        return safe_repo_call(
            self.article_repo,
            "set_article_hidden",
            article_id,
            False,
            default=False,
        )

    def update_report_status(self, article_id: int, status: str) -> None:
        safe_repo_call(
            self.report_repo, "update_report_status", article_id, status
        )

    def get_blocked_articles(self) -> List:
        return safe_repo_call(
            self.article_repo, "get_blocked_articles", default=[]
        )

    def hide_category(self, category_id: int) -> bool:
        return safe_repo_call(
            self.category_repo,
            "set_category_hidden",
            category_id,
            True,
            default=False,
        )

    def unhide_category(self, category_id: int) -> bool:
        return safe_repo_call(
            self.category_repo,
            "set_category_hidden",
            category_id,
            False,
            default=False,
        )

    def add_keyword_filter(self, keyword: str) -> bool:
        return safe_repo_call(
            self.keyword_repo, "add_keyword", keyword, default=False
        )

    def block_keyword(self, keyword: str) -> bool:
        return safe_repo_call(
            self.keyword_repo, "block_keyword", keyword, default=False
        )

    def unblock_keyword(self, keyword: str) -> bool:
        return safe_repo_call(
            self.keyword_repo, "unblock_keyword", keyword, default=False
        )

    def delete_keyword(self, keyword: str) -> bool:
        return safe_repo_call(
            self.keyword_repo, "delete_keyword", keyword, default=False
        )

    def get_all_keywords(
        self, active_only: bool = True
    ) -> List[KeywordFilter]:
        return safe_repo_call(
            self.keyword_repo,
            "get_all_keywords",
            active_only=active_only,
            default=[],
        )
