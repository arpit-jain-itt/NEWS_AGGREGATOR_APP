from dataclasses import asdict
from flask_restx import Namespace, Resource, fields
from server.repository.category_repository import CategoryRepository
from server.repository.db_connector import db
from server.utils.response_formatter import format_response
from server.utils.auth import require_role

api = Namespace("categories", description="Category operations")
category_repo = CategoryRepository(db)

add_category_model = api.model(
    "AddCategory",
    {"name": fields.String(required=True, description="Category name")},
)


def serialize_category(cat):
    d = asdict(cat)
    if d.get("updated_at"):
        d["updated_at"] = d["updated_at"].isoformat()
    return d


@api.route("")
class CategoryCollection(Resource):
    def get(self):
        categories = category_repo.get_all_categories()
        data = [serialize_category(cat) for cat in categories]
        return format_response(data, status_code=200)

    @require_role("admin")
    @api.expect(add_category_model)
    def post(self):
        name = (api.payload or {}).get("name", "").strip()
        if not name:
            return format_response(
                None, success=False, message="name is required", status_code=400
            )

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
