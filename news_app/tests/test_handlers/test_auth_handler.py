import pytest
from unittest.mock import patch
from client.handlers.auth_handler import AuthHandler


@pytest.fixture
def handler():
    return AuthHandler()


def test_login_success(handler):
    fake_user = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False,
    }

    class FakeResp:
        status_code = 200

        def json(self):
            return {"data": fake_user}

    with patch(
        "client.handlers.auth_handler.post_json", return_value=FakeResp()
    ), patch("builtins.input", return_value="test@example.com"), patch(
        "getpass.getpass", return_value="Password123"
    ):
        user = handler.login()
        print("test_login_success: user =", user)
        assert user == fake_user


def test_login_invalid_email(handler):
    with patch("builtins.input", return_value="not-an-email"), patch(
        "getpass.getpass", return_value="Password123"
    ):
        user = handler.login()
        print("test_login_invalid_email: user =", user)
        assert user is None


def test_login_invalid_credentials(handler):
    class FakeResp:
        status_code = 401

        def json(self):
            return {}

    with patch(
        "client.handlers.auth_handler.post_json", return_value=FakeResp()
    ), patch("builtins.input", return_value="test@example.com"), patch(
        "getpass.getpass", return_value="wrongpassword"
    ):
        user = handler.login()
        print("test_login_invalid_credentials: user =", user)
        assert user is None


def test_register_success(handler):
    class FakeResp:
        status_code = 201

        def json(self):
            return {}

    with patch(
        "client.handlers.auth_handler.post_json", return_value=FakeResp()
    ), patch("builtins.input", side_effect=["newuser", "new@example.com"]), patch(
        "getpass.getpass", side_effect=["Password123", "Password123"]
    ), patch(
        "client.handlers.auth_handler.validate_email", return_value=True
    ), patch(
        "client.handlers.auth_handler.validate_password", return_value=True
    ):
        handler.register()
        print("test_register_success: Registration should be successful.")


def test_register_duplicate_email(handler):
    class FakeResp:
        status_code = 409

        def json(self):
            return {"message": "Email already registered."}

    with patch(
        "client.handlers.auth_handler.post_json", return_value=FakeResp()
    ), patch("builtins.input", side_effect=["admin", "admin@example.com"]), patch(
        "getpass.getpass", side_effect=["Password123", "Password123"]
    ), patch(
        "client.handlers.auth_handler.validate_email", return_value=True
    ), patch(
        "client.handlers.auth_handler.validate_password", return_value=True
    ):
        handler.register()
        print("test_register_duplicate_email: Should print 'Email already registered.'")


def test_register_invalid_email(handler):
    with patch("builtins.input", side_effect=["user", "not-an-email"]), patch(
        "getpass.getpass", side_effect=["Password123", "Password123"]
    ), patch("client.handlers.auth_handler.validate_email", return_value=False):
        handler.register()
        print("test_register_invalid_email: Should print 'Invalid email format.'")


def test_register_invalid_password(handler):
    with patch("builtins.input", side_effect=["user", "user@example.com"]), patch(
        "getpass.getpass", side_effect=["short", "short"]
    ), patch("client.handlers.auth_handler.validate_email", return_value=True), patch(
        "client.handlers.auth_handler.validate_password", return_value=False
    ):
        handler.register()
        print("test_register_invalid_password: Should print password error.")


def test_register_passwords_do_not_match(handler):
    with patch("builtins.input", side_effect=["user", "user@example.com"]), patch(
        "getpass.getpass", side_effect=["Password123", "Password456"]
    ), patch("client.handlers.auth_handler.validate_email", return_value=True), patch(
        "client.handlers.auth_handler.validate_password", return_value=True
    ):
        handler.register()
        print(
            "test_register_passwords_do_not_match: Should print 'Passwords do not match.'"
        )


def test_logout_success(handler):
    handler.current_user = {"id": 1, "username": "testuser"}

    class FakeResp:
        status_code = 200

    with patch("client.handlers.auth_handler.post_json", return_value=FakeResp()):
        handler.logout()
        print("test_logout_success: Should print 'Logged out successfully.'")


def test_logout_no_user(handler):
    handler.current_user = None
    handler.logout()
    print("test_logout_no_user: Should print 'No user is currently logged in.'")


def test_logout_error(handler):
    handler.current_user = {"id": 1, "username": "testuser"}

    class FakeResp:
        status_code = 500

    with patch("client.handlers.auth_handler.post_json", return_value=FakeResp()):
        handler.logout()
        print("test_logout_error: Should print 'Logout failed.'")


def test_manage_users_list_and_delete(handler):
    handler.current_user = {"id": 1, "username": "admin", "is_admin": True}
    fake_users = [
        {"id": 1, "username": "admin", "email": "admin@example.com", "is_admin": True},
        {"id": 2, "username": "user", "email": "user@example.com", "is_admin": False},
    ]

    class FakeDelResp:
        status_code = 200

    with patch("client.handlers.auth_handler.get_json", return_value=fake_users), patch(
        "builtins.input", side_effect=["1", "2"]
    ), patch("client.handlers.auth_handler.delete_json", return_value=FakeDelResp()):
        handler.manage_users()
        print(
            "test_manage_users_list_and_delete: Should print user list and delete user."
        )


def test_manage_users_no_users(handler):
    handler.current_user = {"id": 1, "username": "admin", "is_admin": True}
    with patch("client.handlers.auth_handler.get_json", return_value=[]):
        handler.manage_users()
        print("test_manage_users_no_users: Should print 'No users found.'")


def test_manage_users_invalid_choice(handler):
    handler.current_user = {"id": 1, "username": "admin", "is_admin": True}
    fake_users = [
        {"id": 1, "username": "admin", "email": "admin@example.com", "is_admin": True},
    ]
    with patch("client.handlers.auth_handler.get_json", return_value=fake_users), patch(
        "builtins.input", side_effect=["3"]
    ):
        handler.manage_users()
        print("test_manage_users_invalid_choice: Should print 'Invalid choice.'")
