from datetime import datetime, timezone
from typing import List, Optional, Callable, Any
from dateutil.parser import parse as parse_datetime


def parse_ts(raw: Optional[str]) -> datetime:
    try:
        return parse_datetime(raw) if raw else datetime.now(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def get_current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


def get_category_id(category_repo, category_name: str) -> int:
    cat = category_repo.get_category_by_name(category_name)
    if cat:
        return cat.id
    return category_repo.get_general_category().id


def filter_by_keywords(
    items: List[Any],
    keywords: List[str],
    fields: List[str] = ["title", "description", "content"],
) -> List[Any]:
    keywords = [kw.lower() for kw in keywords]
    filtered = []
    for item in items:
        text = " ".join(
            str(getattr(item, f, "") or "") for f in fields
        ).lower()
        if any(kw in text for kw in keywords):
            filtered.append(item)
    return filtered


def filter_by_categories(
    items: List[Any], categories: List[str], field: str = "category_name"
) -> List[Any]:
    categories = [c.lower() for c in categories]
    return [
        item
        for item in items
        if getattr(item, field, "").lower() in categories
    ]


def safe_repo_call(
    repo: Optional[Any], method: str, *args, default=None, **kwargs
):
    if repo and hasattr(repo, method):
        return getattr(repo, method)(*args, **kwargs)
    return default


def compose_email_body(username: str, articles: List[Any]) -> str:
    body = (
        f"Hello {username},\n\n"
        "Here are the latest news articles matching your preferences:\n\n"
    )
    for art in articles:
        body += (
            f"- {getattr(art, 'title', '')}\n  {getattr(art, 'url', '')}\n\n"
        )
    body += "Regards,\nNews Aggregator Team"
    return body


def handle_db_exception(func: Callable, *args, **kwargs) -> bool:
    try:
        func(*args, **kwargs)
        return True
    except Exception:
        return False


# Optional Return Helper
def optional_return(value, default=None):
    return value if value is not None else default


def send_email_safely(send_func, *args, **kwargs) -> bool:
    try:
        send_func(*args, **kwargs)
        return True
    except Exception:
        return False
