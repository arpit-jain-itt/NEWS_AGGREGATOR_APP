import getpass
import requests
from client.utils.validators import validate_email, validate_password

SERVER_URL = "http://localhost:5000"


class AuthHandler:
    def __init__(self):
        self.current_user = None  # Track of the logged-in user

    def login(self) -> dict | None:
        print("\n--- Login ---")
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ").strip()

        if not validate_email(email):
            print("Invalid email format.")
            return None

        try:
            response = requests.post(
                f"{SERVER_URL}/api/users/login",
                json={"email": email, "password": password},
            )
            if response.status_code == 200:
                res_json = response.json()
                user = res_json.get("data")
                if not user:
                    print("Login response missing user data.")
                    return None
                self.current_user = user  # Save for the logged-in user
                print(f"Welcome, {user['username']}!")
                return user
            else:
                print("Invalid credentials. Please try again.")
                return None
        except requests.exceptions.ConnectionError:
            print("Server is not running. Please start the server.")
            return None

    def register(self):
        print("\n--- Register ---")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ").strip()
        confirm_password = getpass.getpass("Confirm Password: ").strip()

        if not username:
            print("Username cannot be empty.")
            return

        if not validate_email(email):
            print("Invalid email format.")
            return

        if not validate_password(password):
            print(
                "Password must be at least 8 characters and include uppercase, lowercase, and digits."
            )
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        try:
            response = requests.post(
                f"{SERVER_URL}/api/users/register",
                json={"username": username, "email": email, "password": password},
            )
            if response.status_code in (200, 201):
                print("Registration successful. You can now log in.")
            elif response.status_code in (400, 409):
                try:
                    msg = response.json().get("message", "")
                except ValueError:
                    msg = ""
                if not msg:
                    msg = "Email already registered."
                print(msg)
            else:
                print("Registration failed. Please try again later.")
        except requests.exceptions.ConnectionError:
            print("Server is not running. Please start the server.")

    def logout(self):
        print("\nLogging out...")
        if not self.current_user:
            print("No user is currently logged in.")
            return

        headers = {"X-User-ID": str(self.current_user["id"])}
        try:
            response = requests.post(f"{SERVER_URL}/api/users/logout", headers=headers)
            if response.status_code == 200:
                print("Logged out successfully.")
            else:
                print("Logout failed.")
        except requests.exceptions.ConnectionError:
            print("Server is not running. Please start the server.")

        # Clear current user
        self.current_user = None

    def manage_users(self):
        print("\n--- Manage Users (Admin Only) ---")
        if not self.current_user:
            print("Please log in first.")
            return

        headers = {"X-User-ID": str(self.current_user["id"])}
        try:
            response = requests.get(f"{SERVER_URL}/api/admin/users", headers=headers)
            if response.status_code != 200:
                print("Failed to fetch users.")
                return

            users = response.json().get("data", [])
            if not users:
                print("No users found.")
                return

            print("\n--- User List ---")
            for user in users:
                role = "Admin" if user.get("is_admin") else "User"
                print(
                    f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Role: {role}"
                )

            print("\nOptions:")
            print("1. Delete User")
            print("2. Back")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                user_id = input("Enter user ID to delete: ").strip()
                if not user_id.isdigit():
                    print("Invalid user ID.")
                    return
                del_resp = requests.delete(
                    f"{SERVER_URL}/api/admin/users/{user_id}", headers=headers
                )
                if del_resp.status_code == 200:
                    print("User deleted successfully.")
                else:
                    print("Operation failed. Check user ID or permissions.")
            elif choice == "2":
                return
            else:
                print("Invalid choice.")
        except requests.exceptions.ConnectionError:
            print("Server is not running. Please start the server.")
