import flask
from datetime import datetime
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
    parse_iso_date,
)

api = Namespace("news-articles", description="News Articles operations")

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


@api.route("/headlines")
class Headlines(Resource):
    def get(self):
        args = flask.request.args
        start_str = args.get("start_date")
        end_str = args.get("end_date")
        category = args.get("category", "").strip()
        keyword = args.get("keyword", "").strip()
        keywords = [k.strip() for k in keyword.split(",") if k.strip()]
        limit, offset = get_pagination(args)
        if start_str:
            start_date, err = parse_iso_date(start_str, "start_date")
            if err:
                return format_response({"message": err}, 400, False)
            start_date = start_date.date()
        else:
            start_date = datetime.now().date()
        if end_str:
            end_date, err = parse_iso_date(end_str, "end_date")
            if err:
                return format_response({"message": err}, 400, False)
            end_date = end_date.date()
        else:
            end_date = start_date
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        articles = news_service.search_articles(
            keywords, category, start_dt, end_dt, limit, offset
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
                    "category_name": getattr(a, "category_name", None),
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
        limit, offset = get_pagination(args)
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
                    "category_name": getattr(a, "category_name", None),
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
        limit, offset = get_pagination(args)
        start_dt = end_dt = None
        if start_str:
            start_dt, err = parse_iso_date(start_str, "start_date")
            if err:
                return format_response({"message": err}, 400, False)
        if end_str:
            end_dt, err = parse_iso_date(end_str, "end_date")
            if err:
                return format_response({"message": err}, 400, False)
            if end_dt.time() == datetime.min.time():
                end_dt = datetime.combine(end_dt.date(), datetime.max.time())
        keywords = [k.strip() for k in keyword.split(",") if k.strip()]
        results = news_service.search_articles(
            keywords, category, start_dt, end_dt, limit, offset
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
                    "category_name": getattr(a, "category_name", None),
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


@api.route("/article/<int:article_id>")
class ArticleDetails(Resource):
    def get(self, article_id):
        article = news_service.article_repo.get_article_by_id(
            article_id, include_hidden=True
        )
        if not article:
            return format_response(
                None,
                success=False,
                message="Article not found",
                status_code=404,
            )
        return format_response(
            {
                "id": article.id,
                "title": article.title,
                "description": article.description,
                "content": article.content,
                "url": article.url,
                "published_at": (
                    article.published_at.isoformat() if article.published_at else None
                ),
                "source_id": article.source_id,
                "category_id": article.category_id,
                "is_hidden": article.is_hidden,
                "category_name": getattr(article, "category_name", None),
            },
            status_code=200,
        )


@api.route("/personalized/<int:user_id>")
class PersonalizedNews(Resource):
    def get(self, user_id):
        limit = flask.request.args.get("limit", 10, type=int)
        offset = flask.request.args.get("offset", 0, type=int)
        articles = news_service.get_personalized_articles(user_id, limit, offset)
        return format_response(
            [
                {
                    "id": a["id"],
                    "title": a["title"],
                    "description": a.get("description"),
                    "content": a.get("content"),
                    "url": a.get("url"),
                    "published_at": (
                        a["published_at"].isoformat()
                        if isinstance(a["published_at"], datetime)
                        else a["published_at"]
                    ),
                    "source_id": a.get("source_id"),
                    "category_id": a.get("category_id"),
                    "category_name": a.get("category_name"),
                }
                for a in articles
            ],
            200,
        )
