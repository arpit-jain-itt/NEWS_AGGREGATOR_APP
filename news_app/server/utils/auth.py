import bcrypt
from functools import wraps
from flask import request
from server.repository.user_repository import UserRepository
from server.repository.db_connector import db


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_user_from_request():
    user_id = request.headers.get("X-User-ID")
    return int(user_id) if user_id and user_id.isdigit() else None


def get_user_role(user_id: int) -> str:
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    return "admin" if user and user.is_admin else "user" if user else None


def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_user_from_request()
            if not user_id:
                return {
                    "success": False,
                    "message": "Unauthorized - Missing user ID",
                    "data": None,
                }, 401

            role = get_user_role(user_id)
            if not role or role != required_role:
                return {
                    "success": False,
                    "message": f"Forbidden - Requires '{required_role}' role",
                    "data": None,
                }, 403

            return f(*args, **kwargs)

        return wrapper

    return decorator
