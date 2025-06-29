import flask
from flask_restx import Namespace, Resource
from server.services.news_service import NewsService
from server.repository.article_repository import ArticleRepository
from server.repository.category_repository import CategoryRepository
from server.repository.source_repository import SourceRepository
from server.repository.viewed_article_repository import ViewedArticleRepository
from server.repository.likes_dislikes_repository import LikesDislikesRepository
from server.repository.report_repository import ReportRepository
from server.repository.keyword_filter_repository import KeywordFilterRepository
from server.repository.user_repository import UserRepository
from server.utils.response_formatter import format_response
from server.repository.db_connector import db
from server.utils.controller_helper import (
    get_pagination,
    safe_int,
    require_fields,
)

api = Namespace("news-user", description="News User Interaction operations")

news_service = NewsService(
    ArticleRepository(db),
    CategoryRepository(db),
    SourceRepository(db),
    ViewedArticleRepository(db),
    LikesDislikesRepository(db),
    keyword_repo=KeywordFilterRepository(db),
    report_repo=ReportRepository(db),
    user_repo=UserRepository(db),
)


@api.route("/save")
class SaveArticle(Resource):
    def post(self):
        data = flask.request.get_json()
        ok, err = require_fields(data or {}, ["user_id", "article_id"])
        if not ok:
            return format_response({"message": err}, 400)
        result = news_service.save_article(data["user_id"], data["article_id"])
        if result == "saved":
            return format_response({"message": "Article saved successfully."}, 201)
        if result == "already_saved":
            return format_response({"message": "Article already saved."}, 409)
        return format_response({"message": "Failed to save article."}, 500)

    def delete(self):
        user_id = flask.request.args.get("user_id")
        article_id = flask.request.args.get("article_id")
        ok, err = require_fields(
            {"user_id": user_id, "article_id": article_id},
            ["user_id", "article_id"],
        )
        if not ok:
            return format_response({"message": err}, 400)
        user_id, err1 = safe_int(user_id, "user_id")
        article_id, err2 = safe_int(article_id, "article_id")
        if err1 or err2:
            return format_response({"message": err1 or err2}, 400)
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
        ok, err = require_fields(data or {}, ["user_id", "article_id"])
        if not ok:
            return format_response({"message": err}, 400)
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
        ok, err = require_fields({"user_id": user_id}, ["user_id"])
        if not ok:
            return format_response({"message": err}, 400)
        user_id, err = safe_int(user_id, "user_id")
        if err:
            return format_response({"message": err}, 400)
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
        ok, err = require_fields(data or {}, ["user_id", "article_id", "is_like"])
        if not ok:
            return format_response({"message": err}, 400)
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
        ok, err = require_fields(
            {"user_id": user_id, "article_id": article_id},
            ["user_id", "article_id"],
        )
        if not ok:
            return format_response({"message": err}, 400)
        user_id, err1 = safe_int(user_id, "user_id")
        article_id, err2 = safe_int(article_id, "article_id")
        if err1 or err2:
            return format_response({"message": err1 or err2}, 400)
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
        ok, err = require_fields({"user_id": user_id}, ["user_id"])
        if not ok:
            return format_response({"message": err}, 400)
        user_id, err = safe_int(user_id, "user_id")
        if err:
            return format_response({"message": err}, 400)
        summary = news_service.get_reaction_summary(user_id)
        return format_response(summary, 200)


@api.route("/reactions")
class ReactedArticles(Resource):
    def get(self):
        args = flask.request.args
        user_id = args.get("user_id")
        reaction_type = args.get("type", "like").lower()
        ok, err = require_fields({"user_id": user_id}, ["user_id"])
        if not ok:
            return format_response({"message": err}, 400)
        user_id, err = safe_int(user_id, "user_id")
        if err:
            return format_response({"message": err}, 400)
        if reaction_type not in ("like", "dislike"):
            return format_response({"message": "type must be 'like' or 'dislike'"}, 400)
        limit, offset = get_pagination(args)
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


@api.route("/report")
class ReportArticle(Resource):
    def post(self):
        data = flask.request.get_json()
        ok, err = require_fields(data or {}, ["user_id", "article_id", "reason"])
        if not ok:
            return format_response(
                None,
                success=False,
                message=err,
                status_code=400,
            )
        user_id, err1 = safe_int(data["user_id"], "user_id")
        article_id, err2 = safe_int(data["article_id"], "article_id")
        reason = str(data["reason"])
        if err1 or err2:
            return format_response(
                None,
                success=False,
                message=err1 or err2,
                status_code=400,
            )
        try:
            success = news_service.report_article(user_id, article_id, reason)
            if success:
                return format_response(
                    None, message="Report submitted.", status_code=201
                )
            else:
                return format_response(
                    None, message="Failed to submit report.", status_code=500
                )
        except Exception:
            return format_response(None, message="Error occurred.", status_code=500)
