import flask
from datetime import datetime
from flask_restx import Namespace, Resource
from server.services.news_service import NewsService
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.utils.response_formatter import format_response
from server.repository.db_connector import db

api = Namespace("news", description="News operations")

news_service = NewsService(
    ArticleRepository(db),
    CategoryRepository(db),
    SourceRepository(db),
    ViewedArticleRepository(db),
    LikesDislikesRepository(db),
)


def _get_pagination(args):
    limit = int(args.get("limit", 20))
    if "offset" in args:
        offset = int(args.get("offset", 0))
    else:
        page = int(args.get("page", 1))
        offset = (page - 1) * limit
    return limit, offset


@api.route("/headlines")
class Headlines(Resource):
    def get(self):
        args = flask.request.args
        start_str = args.get("start_date")
        end_str = args.get("end_date")
        limit, offset = _get_pagination(args)
        try:
            start_date = (
                datetime.fromisoformat(start_str).date()
                if start_str
                else datetime.now().date()
            )
            end_date = datetime.fromisoformat(end_str).date() if end_str else start_date
        except ValueError:
            return format_response(
                {"message": "Invalid date format. Use YYYY-MM-DD."}, 400, False
            )
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        articles = news_service.search_articles("", "", start_dt, end_dt, limit, offset)
        return format_response(
            [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                }
                for a in articles
            ],
            200,
        )


@api.route("/latest")
class LatestNews(Resource):
    def get(self):
        args = flask.request.args
        category = args.get("category")
        limit, offset = _get_pagination(args)
        articles = news_service.get_latest_articles(category, limit, offset)
        return format_response(
            [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                }
                for a in articles
            ],
            200,
        )


@api.route("/search")
class SearchArticles(Resource):
    def get(self):
        args = flask.request.args
        keyword = args.get("keyword", "").strip()
        category = args.get("category", "").strip()
        start_str = args.get("start_date")
        end_str = args.get("end_date")
        limit, offset = _get_pagination(args)
        start_dt = end_dt = None
        if start_str:
            try:
                start_dt = datetime.fromisoformat(start_str)
            except ValueError:
                return format_response(
                    {"message": "Invalid start_date. Use YYYY-MM-DD."}, 400, False
                )
        if end_str:
            try:
                end_raw = datetime.fromisoformat(end_str)
                end_dt = (
                    end_raw
                    if end_raw.time() != datetime.min.time()
                    else datetime.combine(end_raw.date(), datetime.max.time())
                )
            except ValueError:
                return format_response(
                    {"message": "Invalid end_date. Use YYYY-MM-DD."}, 400, False
                )
        results = news_service.search_articles(
            keyword, category, start_dt, end_dt, limit, offset
        )
        return format_response(
            [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                }
                for a in results
            ],
            200,
        )


@api.route("/categories")
class NewsCategories(Resource):
    def get(self):
        categories = news_service.category_repo.get_all_categories()
        return format_response([{"id": c.id, "name": c.name} for c in categories], 200)


@api.route("/save")
class SaveArticle(Resource):
    def post(self):
        data = flask.request.get_json()
        if not data or "user_id" not in data or "article_id" not in data:
            return format_response(
                {"message": "user_id and article_id are required"}, 400
            )
        result = news_service.save_article(data["user_id"], data["article_id"])
        if result == "saved":
            return format_response({"message": "Article saved successfully."}, 201)
        if result == "already_saved":
            return format_response({"message": "Article already saved."}, 409)
        return format_response({"message": "Failed to save article."}, 500)

    def delete(self):
        user_id = flask.request.args.get("user_id")
        article_id = flask.request.args.get("article_id")
        if not user_id or not article_id:
            return format_response(
                {"message": "user_id and article_id are required"}, 400
            )
        try:
            user_id = int(user_id)
            article_id = int(article_id)
        except ValueError:
            return format_response(
                {"message": "user_id and article_id must be integers"}, 400
            )
        result = news_service.remove_saved_article(user_id, article_id)
        if result == "deleted":
            return format_response({"message": "Article removed successfully."}, 200)
        if result == "not_found":
            return format_response({"message": "Saved article not found."}, 404)
        return format_response({"message": "Failed to remove article."}, 500)


@api.route("/viewed")
class MarkArticleViewed(Resource):
    def post(self):
        data = flask.request.get_json()
        if not data or "user_id" not in data or "article_id" not in data:
            return format_response(
                {"message": "user_id and article_id are required"}, 400
            )
        try:
            news_service.mark_article_viewed(data["user_id"], data["article_id"])
            return format_response({"message": "Article marked as viewed."}, 200)
        except Exception:
            return format_response(
                {"message": "Failed to mark article as viewed."}, 500
            )


@api.route("/saved")
class SavedArticles(Resource):
    def get(self):
        user_id = flask.request.args.get("user_id")
        if not user_id:
            return format_response({"message": "user_id is required"}, 400)
        try:
            user_id = int(user_id)
        except ValueError:
            return format_response({"message": "user_id must be an integer"}, 400)
        saved_articles = news_service.get_saved_articles_by_user(user_id)
        return format_response(
            [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                }
                for a in saved_articles
            ],
            200,
        )


@api.route("/react")
class ArticleReaction(Resource):
    def post(self):
        data = flask.request.get_json()
        if not data or {"user_id", "article_id", "is_like"} - data.keys():
            return format_response(
                {"message": "user_id, article_id and is_like are required"}, 400
            )
        result = news_service.react_to_article(
            data["user_id"], data["article_id"], bool(data["is_like"])
        )
        if result == "created":
            return format_response({"message": "Reaction created."}, 201)
        if result == "deleted":
            return format_response({"message": "Reaction removed."}, 200)
        return format_response({"message": "Failed to save reaction."}, 500)

    def delete(self):
        user_id = flask.request.args.get("user_id")
        article_id = flask.request.args.get("article_id")
        if not user_id or not article_id:
            return format_response(
                {"message": "user_id and article_id are required"}, 400
            )
        try:
            user_id = int(user_id)
            article_id = int(article_id)
        except ValueError:
            return format_response(
                {"message": "user_id and article_id must be integers"}, 400
            )
        result = news_service.remove_reaction(user_id, article_id)
        if result == "deleted":
            return format_response({"message": "Reaction removed."}, 200)
        if result == "not_found":
            return format_response({"message": "Reaction not found."}, 404)
        return format_response({"message": "Failed to remove reaction."}, 500)


@api.route("/reactions/summary")
class ReactionSummary(Resource):
    def get(self):
        user_id = flask.request.args.get("user_id")
        if not user_id:
            return format_response({"message": "user_id is required"}, 400)
        try:
            user_id = int(user_id)
        except ValueError:
            return format_response({"message": "user_id must be an integer"}, 400)
        summary = news_service.get_reaction_summary(user_id)
        return format_response(summary, 200)


@api.route("/reactions")
class ReactedArticles(Resource):
    def get(self):
        args = flask.request.args
        user_id = args.get("user_id")
        reaction_type = args.get("type", "like").lower()
        if not user_id:
            return format_response({"message": "user_id is required"}, 400)
        try:
            user_id = int(user_id)
        except ValueError:
            return format_response({"message": "user_id must be an integer"}, 400)
        if reaction_type not in ("like", "dislike"):
            return format_response({"message": "type must be 'like' or 'dislike'"}, 400)
        limit, offset = _get_pagination(args)
        articles = news_service.get_reacted_articles(
            user_id, reaction_type, limit, offset
        )
        return format_response(
            [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "source_id": a.source_id,
                    "category_id": a.category_id,
                }
                for a in articles
            ],
            200,
        )


@api.route("/reactions/article/<int:article_id>")
class ArticleReactionCounts(Resource):
    def get(self, article_id):
        counts = news_service.get_article_reactions_count(article_id)
        if counts is None:
            return format_response({"message": "Article not found."}, 404)
        return format_response(counts, 200)
