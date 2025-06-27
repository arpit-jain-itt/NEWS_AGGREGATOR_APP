from flask_restx import Namespace, Resource
from flask import request as flask_request
from server.repository.notification_repository import NotificationRepository
from server.repository.category_repository import CategoryRepository
from server.utils.response_formatter import format_response
from server.repository.db_connector import db
from server.utils.notification_pref_codec import (
    encode_preferences,
    decode_preferences,
)
from server.utils.controller_helper import (
    require_fields,
    safe_int,
)

api = Namespace("notifications", description="Notification operations")

notification_repo = NotificationRepository(db)
category_repo = CategoryRepository(db)


@api.route("/preferences")
class NotificationPreferences(Resource):
    def get(self):
        user_id = flask_request.args.get("user_id")
        ok, err = require_fields({"user_id": user_id}, ["user_id"])
        if not ok:
            return format_response({"message": err}, status_code=400)
        user_id, err = safe_int(user_id, "user_id")
        if err:
            return format_response({"message": err}, status_code=400)

        prefs = notification_repo.get_notification_preferences(user_id)
        if not prefs:
            return format_response(
                {"message": "No notification preferences found for user."},
                status_code=404,
            )

        decoded = decode_preferences(prefs["keywords"])
        response_payload = {
            "categories": decoded["categories"],
            "keywords": decoded["keywords"],
            "notify_via_email": prefs["notify_via_email"],
            "enabled": prefs["enabled"],
        }
        return format_response(response_payload, status_code=200)

    def post(self):
        data = flask_request.get_json()
        ok, err = require_fields(data or {}, ["user_id"])
        if not ok:
            return format_response({"message": err}, status_code=400)
        user_id, err = safe_int(data["user_id"], "user_id")
        if err:
            return format_response({"message": err}, status_code=400)

        existing = notification_repo.get_notification_preferences(user_id) or {}
        decoded_existing = decode_preferences(existing.get("keywords", ""))

        categories_csv = data.get(
            "categories",
            ",".join(decoded_existing["categories"]),
        )
        keywords_csv = data.get(
            "keywords",
            ",".join(decoded_existing["keywords"]),
        )
        notify_via_email = data.get(
            "notify_via_email", existing.get("notify_via_email", True)
        )
        enabled = data.get("enabled", existing.get("enabled", True))

        valid_set = {cat.name.lower() for cat in category_repo.get_all_categories()}
        user_cats = [c.strip().lower() for c in categories_csv.split(",") if c.strip()]
        invalid = [c for c in user_cats if c not in valid_set]

        if invalid:
            return format_response(
                {
                    "message": "Invalid categories",
                    "invalid_categories": invalid,
                    "valid_categories": sorted(valid_set),
                },
                status_code=400,
                success=False,
            )

        cleaned_categories_csv = ",".join(user_cats)

        encoded_blob = encode_preferences(cleaned_categories_csv, keywords_csv)
        result = notification_repo.update_notification_preferences(
            user_id, encoded_blob, notify_via_email, enabled
        )
        if result:
            return format_response(
                {"message": "Notification preferences updated successfully."},
                status_code=200,
            )
        return format_response(
            {"message": "Failed to update notification preferences."}, status_code=500
        )
