import pytest
from flask import Flask, session, jsonify, request

app = Flask(__name__)
app.secret_key = "test-secret-key"


# Dummy admin decorator
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("user_id") or not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/api/admin/set-active-source", methods=["POST"])
@admin_required
def set_active_source():
    data = request.get_json()
    source_id = data.get("source_id")
    if not source_id:
        return jsonify({"error": "Missing source_id"}), 400
    return jsonify({"message": "Source set active"}), 200


@app.route("/api/admin/users", methods=["GET"])
@admin_required
def list_users():
    return (
        jsonify(
            [
                {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "is_admin": True,
                },
                {
                    "id": 2,
                    "username": "user",
                    "email": "user@example.com",
                    "is_admin": False,
                },
            ]
        ),
        200,
    )


@app.route("/api/admin/fetch-news", methods=["POST"])
@admin_required
def fetch_news():
    return jsonify({"message": "News fetched successfully"}), 200


@app.route("/api/admin/news-sources", methods=["GET"])
@admin_required
def get_news_sources():
    return jsonify([{"id": 1, "name": "BBC"}, {"id": 2, "name": "CNN"}]), 200


@app.route("/api/admin/news-sources/<int:source_id>", methods=["DELETE"])
@admin_required
def remove_source(source_id):
    return jsonify({"message": f"Source {source_id} removed"}), 200


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def login_as_admin(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["is_admin"] = True


def test_set_active_source_success(client, login_as_admin):
    res = client.post("/api/admin/set-active-source", json={"source_id": 1})
    print("\n test_set_active_source_success:", res.get_json())
    assert res.status_code == 200
    assert res.get_json()["message"] == "Source set active"


def test_set_active_source_missing_id(client, login_as_admin):
    res = client.post("/api/admin/set-active-source", json={})
    print("\n test_set_active_source_missing_id:", res.get_json())
    assert res.status_code == 400
    assert "Missing source_id" in res.get_json()["error"]


def test_list_users(client, login_as_admin):
    res = client.get("/api/admin/users")
    users = res.get_json()
    print("\n test_list_users:", users)
    assert res.status_code == 200
    assert isinstance(users, list)
    assert users[0]["is_admin"] is True


def test_fetch_news(client, login_as_admin):
    res = client.post("/api/admin/fetch-news")
    print("\n test_fetch_news:", res.get_json())
    assert res.status_code == 200
    assert res.get_json()["message"] == "News fetched successfully"


def test_news_sources_flow(client, login_as_admin):
    res = client.get("/api/admin/news-sources")
    sources = res.get_json()
    print("\n test_news_sources_flow:", sources)
    assert res.status_code == 200
    assert isinstance(sources, list)
    assert any(source["name"] == "BBC" for source in sources)


def test_remove_source(client, login_as_admin):
    res = client.delete("/api/admin/news-sources/1")
    print("\n test_remove_source:", res.get_json())
    assert res.status_code == 200
    assert "removed" in res.get_json()["message"]
