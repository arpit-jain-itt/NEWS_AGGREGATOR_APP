import requests

SERVER_URL = "http://localhost:5000"


def get_json(route, params=None, headers=None, default=None):
    try:
        resp = requests.get(
            f"{SERVER_URL}{route}", params=params, headers=headers
        )
        return resp.json().get("data", default)
    except requests.exceptions.ConnectionError:
        print("Server is not running.")
        return default
    except Exception:
        print("GET failed or server unavailable.")
        return default


def post_json(route, payload=None, headers=None):
    try:
        return requests.post(
            f"{SERVER_URL}{route}", json=payload, headers=headers
        )
    except requests.exceptions.ConnectionError:
        print("Server is not running.")
        return None
    except Exception:
        print("POST failed or server unavailable.")
        return None


def delete_json(route, payload=None, headers=None):
    try:
        if payload:
            return requests.delete(
                f"{SERVER_URL}{route}", json=payload, headers=headers
            )
        else:
            return requests.delete(f"{SERVER_URL}{route}", headers=headers)
    except requests.exceptions.ConnectionError:
        print("Server is not running.")
        return None
    except Exception:
        print("DELETE failed or server unavailable.")
        return None


def extract_data(resp, default=None):
    try:
        return resp.json().get("data", default)
    except Exception:
        return default


def prompt_choice(prompt, choices):
    choice = input(prompt).strip()
    while choice not in choices:
        print("Invalid choice.")
        choice = input(prompt).strip()
    return choice


def prompt_yes_no(prompt, default=True):
    val = input(prompt).strip().lower()
    if val == "":
        return default
    return val == "y"


def prompt_nonempty(prompt):
    val = input(prompt).strip()
    while not val:
        print("Input cannot be empty.")
        val = input(prompt).strip()
    return val


def prompt_int(prompt, min_value=None, max_value=None):
    while True:
        val = input(prompt).strip()
        if not val.isdigit():
            print("Please enter a valid number.")
            continue
        num = int(val)
        if min_value is not None and num < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and num > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return num


def print_article_row(article, idx):
    title = article.get("title", "[No Title]")
    pub = article.get("published_at", "N/A")
    print(f"{idx}. {title} ({pub})")


def print_article_details(article):
    print("\n--- Article Details ---")
    for label, key in [
        ("Title", "title"),
        ("Published At", "published_at"),
        ("Description", "description"),
        ("Content", "content"),
        ("URL", "url"),
        ("Category", "category_name"),
    ]:
        print(f"{label}: {article.get(key, 'N/A')}")
    print()


def menu_loop(options, prompt="Choose an option: ", back_option="Back"):
    while True:
        print("\n--- Menu ---")
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        print(f"b. {back_option}")
        choice = input(prompt).strip().lower()
        if choice == "b":
            break
        if choice in options:
            options[choice][1]()
        else:
            print("Invalid choice.")
