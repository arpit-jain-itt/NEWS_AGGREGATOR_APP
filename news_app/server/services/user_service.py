from server.repository.user_repository import UserRepository
from server.repository.report_repository import ReportRepository
from server.utils.auth import hash_password, verify_password
from server.models.user_model import User
from server.models.report_model import Report
from typing import Optional, List
from server.utils.service_helper import safe_repo_call


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        report_repo: Optional[ReportRepository] = None,
    ):
        self.user_repo = user_repo
        self.report_repo = report_repo

    def register_user(
        self, username: str, email: str, password: str, is_admin=False
    ) -> Optional[int]:
        existing_user = safe_repo_call(
            self.user_repo, "get_user_by_email", email
        )
        if existing_user:
            return None
        password_hash = hash_password(password)
        user_id = safe_repo_call(
            self.user_repo,
            "create_user",
            username,
            email,
            password_hash,
            is_admin,
        )
        return user_id

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = safe_repo_call(self.user_repo, "get_user_by_email", email)
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        return safe_repo_call(self.user_repo, "get_user_by_email", email)

    def get_user(self, user_id: int) -> Optional[User]:
        return safe_repo_call(self.user_repo, "get_user_by_id", user_id)

    def list_users(self):
        return safe_repo_call(self.user_repo, "get_all_users", default=[])

    def delete_user(self, user_id: int) -> bool:
        return safe_repo_call(
            self.user_repo, "delete_user", user_id, default=False
        )

    def get_user_reports(self, user_id: int) -> Optional[List[Report]]:
        return safe_repo_call(
            self.report_repo, "get_reports_by_user", user_id, default=None
        )

    def remove_user_report(self, user_id: int, article_id: int) -> bool:
        return safe_repo_call(
            self.report_repo,
            "remove_report",
            user_id,
            article_id,
            default=False,
        )
