import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, jsonify
from flask_restx import Api
from server.controllers.user_controller import api as user_ns
from server.controllers.admin_controller import api as admin_ns
from server.controllers.news_controller import api as news_ns
from server.controllers.notification_controller import api as notifications_ns
from server.controllers.category_controller import api as category_ns

import secrets

os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/server.log"
LOG_LEVEL = logging.INFO

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
handler.setLevel(LOG_LEVEL)

logging.basicConfig(level=LOG_LEVEL, handlers=[handler])


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    # test auth for swagger
    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        },
        "User ID": {
            "type": "apiKey",
            "in": "header",
            "name": "X-User-ID",
        },
    }

    api = Api(
        app,
        version="1.0",
        title="News Aggregator API",
        description="API for News Aggregator",
        doc="/swagger",
        authorizations=authorizations,
        security=["Bearer Auth", "User ID"],
    )

    api.add_namespace(user_ns, path="/api/users")
    api.add_namespace(admin_ns, path="/api/admin")
    api.add_namespace(news_ns, path="/api/news")
    api.add_namespace(notifications_ns, path="/api/notifications")
    api.add_namespace(category_ns, path="/api/categories")

    # Adding basic healkth check
    @app.route("/health", methods=["GET"])
    def health_check():
        return "OK", 200

    # Global error handling
    @app.errorhandler(Exception)
    def handle_error(error):
        logging.error("Unhandled error: %s", error, exc_info=True)
        return (
            jsonify({"success": False, "message": "Internal server error."}),
            500,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
