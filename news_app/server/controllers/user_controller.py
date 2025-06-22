from flask import session, request
from flask_restx import Namespace, Resource, fields
from server.services.user_service import UserService
from server.repository.user_repository import UserRepository
from server.repository.report_repository import ReportRepository
from server.utils.response_formatter import format_response
from server.repository.db_connector import DBConnector
from server.utils.auth import require_role

db = DBConnector()
user_service = UserService(UserRepository(db), ReportRepository(db))
api = Namespace("user", description="User operations")

register_model = api.model(
    "RegisterUser",
    {
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)

login_model = api.model(
    "LoginUser",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)


@api.route("/register")
class Register(Resource):
    @api.expect(register_model)
    def post(self):
        data = api.payload
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not all([username, email, password]):
            return format_response(
                None, success=False, message="Missing required fields", status_code=400
            )

        user_id = user_service.register_user(username, email, password)
        if user_id is None:
            return format_response(
                None, success=False, message="Email already exists", status_code=400
            )
        return format_response(
            {"user_id": user_id},
            message="User registered successfully",
            status_code=201,
        )


@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload
        email = data.get("email")
        password = data.get("password")
        if not all([email, password]):
            return format_response(
                None,
                success=False,
                message="Missing email or password",
                status_code=400,
            )

        user = user_service.authenticate_user(email, password)
        if not user:
            return format_response(
                None,
                success=False,
                message="Invalid email or password",
                status_code=401,
            )

        # Store user ID in session
        session["user_id"] = user.id

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }
        return format_response(user_data, message="Login successful", status_code=200)


@api.route("/logout")
class Logout(Resource):
    def post(self):
        session.pop("user_id", None)

        # to print user value as per session
        header_uid = request.headers.get("X-User-ID")
        if header_uid:
            print(f"User {header_uid} logged out via /logout")

        return format_response(None, message="Logged out successfully", status_code=200)


@api.route("/users")
class UserList(Resource):
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
        return format_response(users_data, status_code=200)


@api.route("/my-reports")
class MyReports(Resource):
    def get(self):
        header_uid = request.headers.get("X-User-ID")
        if not header_uid:
            return format_response(
                None, success=False, message="Not logged in", status_code=401
            )
        try:
            user_id = int(header_uid)
        except ValueError:
            return format_response(
                None, success=False, message="Invalid user ID", status_code=400
            )
        reports = user_service.get_user_reports(user_id)
        if reports is None:
            return format_response([], message="No reports found", status_code=200)

        def serialize_report(report):
            d = report.__dict__.copy()
            if d.get("created_at") and hasattr(d["created_at"], "isoformat"):
                d["created_at"] = d["created_at"].isoformat()
            return d

        return format_response([serialize_report(r) for r in reports], status_code=200)

    def delete(self):
        header_uid = request.headers.get("X-User-ID")
        if not header_uid:
            return format_response(
                None, success=False, message="Not logged in", status_code=401
            )
        try:
            user_id = int(header_uid)
        except ValueError:
            return format_response(
                None, success=False, message="Invalid user ID", status_code=400
            )
        data = request.get_json() or {}
        article_id = data.get("article_id")
        if not article_id:
            return format_response(
                None, success=False, message="article_id is required", status_code=400
            )
        try:
            article_id = int(article_id)
        except ValueError:
            return format_response(
                None, success=False, message="Invalid article_id", status_code=400
            )
        success = user_service.remove_user_report(user_id, article_id)
        if success:
            return format_response(
                None, message="Report removed successfully.", status_code=200
            )
        else:
            return format_response(
                None, success=False, message="Failed to remove report.", status_code=500
            )
