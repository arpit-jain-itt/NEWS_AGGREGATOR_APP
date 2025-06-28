from flask_restx import Namespace, Resource, fields
from dataclasses import asdict
from server.services.user_service import UserService
from server.services.news_service import NewsService
from server.services.admin_service import AdminService
from server.repository.user_repository import UserRepository
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.repository.report_repository import ReportRepository
from server.repository.keyword_filter_repository import KeywordFilterRepository
from server.repository.db_connector import db
from server.utils.auth import require_role
from server.utils.controller_helper import (
    require_fields,
    safe_int,
)

user_service = UserService(UserRepository(db))
api = Namespace("admin", description="Admin operations")

news_service = NewsService(
    ArticleRepository(db),
    CategoryRepository(db),
    SourceRepository(db),
    ViewedArticleRepository(db),
    LikesDislikesRepository(db),
    keyword_repo=KeywordFilterRepository(db),
    report_repo=ReportRepository(db),
)

source_repo = SourceRepository(db)
admin_service = AdminService(
    ArticleRepository(db),
    CategoryRepository(db),
    ReportRepository(db),
    KeywordFilterRepository(db),
)

set_active_source_model = api.model(
    "SetActiveSource",
    {
        "source_id": fields.Integer(required=True),
    },
)


@api.route("/fetch-news")
class FetchNews(Resource):
    @require_role("admin")
    def post(self):
        news_service.fetch_and_store_news()
        return {"message": "News fetching started"}, 200


@api.route("/set-active-source")
class SetActiveSource(Resource):
    @require_role("admin")
    @api.expect(set_active_source_model)
    def post(self):
        data = api.payload
        ok, err = require_fields(data or {}, ["source_id"])
        if not ok:
            return {"message": err, "success": False}, 400
        source_id, err = safe_int(data.get("source_id"), "source_id")
        if err:
            return {"message": err, "success": False}, 400

        success = source_repo.set_active_source(source_id)
        if not success:
            return (
                {"message": "Failed to set active source", "success": False},
                400,
            )

        return {"message": "Active source updated"}, 200


@api.route("/users")
class AdminUserList(Resource):
    @require_role("admin")
    def get(self):
        users = user_service.list_users()
        users_data = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_admin": u.is_admin,
            }
            for u in users
        ]
        return {"data": users_data}, 200


@api.route("/news-sources")
class NewsSourceCollection(Resource):
    @require_role("admin")
    def get(self):
        sources = source_repo.get_all_sources()
        data = [
            {
                **asdict(src),
                "last_accessed": (
                    src.last_accessed.isoformat()
                    if src.last_accessed
                    else None
                ),
            }
            for src in sources
        ]
        return {"data": data}, 200

    @require_role("admin")
    def post(self):
        name = (api.payload or {}).get("name")
        ok, err = require_fields({"name": name}, ["name"])
        if not ok:
            return {"message": err}, 400
        if not source_repo.add_source(name):
            return {"message": "Source may already exist"}, 409
        return {"message": "Source added"}, 201


@api.route("/news-sources/<int:source_id>")
class NewsSourceItem(Resource):
    @require_role("admin")
    def delete(self, source_id):
        if source_repo.remove_source(source_id):
            return {"message": "Source removed"}, 200
        return {"message": "Source not found"}, 404


@api.route("/reported-articles")
class ReportedArticles(Resource):
    @require_role("admin")
    def get(self):
        reported = admin_service.get_reported_articles()
        return {"data": reported}, 200


@api.route("/blocked-articles")
class BlockedArticles(Resource):
    @require_role("admin")
    def get(self):
        blocked = admin_service.get_blocked_articles()
        return {
            "data": [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": (
                        a.published_at.isoformat() if a.published_at else None
                    ),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                    "is_hidden": a.is_hidden,
                    "category_name": getattr(a, "category_name", None),
                }
                for a in blocked
            ]
        }, 200


@api.route("/reports/<int:article_id>")
class ArticleReports(Resource):
    @require_role("admin")
    def get(self, article_id):
        reports = admin_service.get_reports_for_article(article_id)
        return {"data": [asdict(r) for r in reports]}, 200


@api.route("/hide-article/<int:article_id>")
class HideArticle(Resource):
    @require_role("admin")
    def post(self, article_id):
        if admin_service.hide_article(article_id):
            admin_service.update_report_status(article_id, "reviewed")
            return {"message": "Article hidden"}, 200
        return {"message": "Failed to hide article"}, 400


@api.route("/unhide-article/<int:article_id>")
class UnhideArticle(Resource):
    @require_role("admin")
    def post(self, article_id):
        if admin_service.unhide_article(article_id):
            return {"message": "Article unhidden"}, 200
        return {"message": "Failed to unhide article"}, 400


@api.route("/hide-category/<int:category_id>")
class HideCategory(Resource):
    @require_role("admin")
    def post(self, category_id):
        if admin_service.hide_category(category_id):
            return {"message": "Category hidden"}, 200
        return {"message": "Failed to hide category"}, 400


@api.route("/unhide-category/<int:category_id>")
class UnhideCategory(Resource):
    @require_role("admin")
    def post(self, category_id):
        if admin_service.unhide_category(category_id):
            return {"message": "Category unhidden"}, 200
        return {"message": "Failed to unhide category"}, 400


@api.route("/keywords")
class KeywordList(Resource):
    @require_role("admin")
    def get(self):
        keywords = admin_service.get_all_keywords(active_only=False)

        def serialize_keyword(k):
            d = asdict(k)
            if d.get("created_at") and hasattr(d["created_at"], "isoformat"):
                d["created_at"] = d["created_at"].isoformat()
            if d.get("updated_at") and hasattr(d["updated_at"], "isoformat"):
                d["updated_at"] = d["updated_at"].isoformat()
            return d

        return {"data": [serialize_keyword(k) for k in keywords]}, 200

    @require_role("admin")
    def post(self):
        keyword = (api.payload or {}).get("keyword")
        ok, err = require_fields({"keyword": keyword}, ["keyword"])
        if not ok:
            return {"message": err}, 400
        if admin_service.add_keyword_filter(keyword):
            return {"message": "Keyword added"}, 201
        return {"message": "Failed to add keyword"}, 400


@api.route("/block-keyword")
class BlockKeyword(Resource):
    @require_role("admin")
    def post(self):
        keyword = (api.payload or {}).get("keyword")
        ok, err = require_fields({"keyword": keyword}, ["keyword"])
        if not ok:
            return {"message": err}, 400
        if admin_service.block_keyword(keyword):
            return {"message": "Keyword blocked"}, 200
        return {"message": "Failed to block keyword"}, 400


@api.route("/unblock-keyword")
class UnblockKeyword(Resource):
    @require_role("admin")
    def post(self):
        keyword = (api.payload or {}).get("keyword")
        ok, err = require_fields({"keyword": keyword}, ["keyword"])
        if not ok:
            return {"message": err}, 400
        if admin_service.unblock_keyword(keyword):
            return {"message": "Keyword unblocked"}, 200
        return {"message": "Failed to unblock keyword"}, 400


@api.route("/delete-keyword")
class DeleteKeyword(Resource):
    @require_role("admin")
    def post(self):
        keyword = (api.payload or {}).get("keyword")
        ok, err = require_fields({"keyword": keyword}, ["keyword"])
        if not ok:
            return {"message": err}, 400
        if admin_service.delete_keyword(keyword):
            return {"message": "Keyword deleted"}, 200
        return {"message": "Failed to delete keyword"}, 400
