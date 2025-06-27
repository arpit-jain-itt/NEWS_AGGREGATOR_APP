from flask_restx import Namespace, Resource, fields
from server.repository.category_repository import CategoryRepository
from server.repository.db_connector import db
from server.utils.response_formatter import format_response
from server.utils.auth import require_role
from server.utils.controller_helper import (
    require_fields,
    serialize_list,
)

api = Namespace("categories", description="Category operations")
category_repo = CategoryRepository(db)

add_category_model = api.model(
    "AddCategory",
    {"name": fields.String(required=True, description="Category name")},
)


@api.route("")
class CategoryCollection(Resource):
    def get(self):
        categories = category_repo.get_all_categories()
        data = serialize_list(categories)
        return format_response(data, status_code=200)

    @require_role("admin")
    @api.expect(add_category_model)
    def post(self):
        name = (api.payload or {}).get("name", "").strip()
        ok, err = require_fields({"name": name}, ["name"])
        if not ok:
            return format_response(None, success=False, message=err, status_code=400)

        success = category_repo.add_category(name)
        if success:
            return format_response(None, message="Category added", status_code=201)

        return format_response(
            None,
            success=False,
            message="Category already exists",
            status_code=409,
        )


@api.route("/<int:category_id>")
@api.param("category_id", "ID of the category")
class CategoryItem(Resource):
    @require_role("admin")
    def delete(self, category_id):
        if category_repo.delete_category_by_id(category_id):
            return format_response(None, message="Category deleted", status_code=200)

        return format_response(
            None,
            success=False,
            message="Category not found or could not be deleted",
            status_code=404,
        )


@api.route("/admin/categories")
class AdminCategoryList(Resource):
    @require_role("admin")
    def get(self):
        categories = category_repo.get_all_categories(include_hidden=True)
        data = serialize_list(categories)
        return format_response(data, status_code=200)
