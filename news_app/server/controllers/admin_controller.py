from flask_restx import Namespace, Resource, fields
from dataclasses import asdict
from server.services.user_service import UserService
from server.services.news_service import NewsService
from server.repository.user_repository import UserRepository
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.repository.db_connector import db
from server.utils.auth import require_role

user_service = UserService(UserRepository(db))
api = Namespace("admin", description="Admin operations")

news_service = NewsService(
    ArticleRepository(db),
    CategoryRepository(db),
    SourceRepository(db),
    ViewedArticleRepository(db),
    LikesDislikesRepository(db),
)

source_repo = SourceRepository(db)

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
        source_id = data.get("source_id")
        if source_id is None:
            return {"message": "source_id is required", "success": False}, 400

        success = source_repo.set_active_source(source_id)
        if not success:
            return {"message": "Failed to set active source", "success": False}, 400

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
                    src.last_accessed.isoformat() if src.last_accessed else None
                ),
            }
            for src in sources
        ]
        return {"data": data}, 200

    @require_role("admin")
    def post(self):
        name = (api.payload or {}).get("name")
        if not name:
            return {"message": "name is required"}, 400
        if not source_repo.add_source(name):
            return {"message": "Source may already exist"}, 409
        return {"message": "Source added"}, 201


# for removal of source
@api.route("/news-sources/<int:source_id>")
class NewsSourceItem(Resource):
    @require_role("admin")
    def delete(self, source_id):
        if source_repo.remove_source(source_id):
            return {"message": "Source removed"}, 200
        return {"message": "Source not found"}, 404
