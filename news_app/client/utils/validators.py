import re


def validate_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(email_regex, email))


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def validate_categories(
    input_str: str, valid_categories: list[str]
) -> tuple[bool, list[str], list[str]]:
    cleaned = []
    for cat in input_str.split(","):
        cat = cat.strip().lower()
        if cat:
            cleaned.append(cat)
    invalid = []
    for cat in cleaned:
        if cat not in valid_categories:
            invalid.append(cat)
    return (len(invalid) == 0, cleaned, invalid)
