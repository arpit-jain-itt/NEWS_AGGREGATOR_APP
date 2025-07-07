import json
from typing import List, Dict


def _split_csv(raw: str) -> List[str]:
    # Spliting a comma-separated string, strip whitespace,
    # drop empties, lower‑case
    raw_str = raw or ""
    parts = raw_str.split(",")
    cleaned = []
    for part in parts:
        stripped = part.strip()
        if stripped:
            cleaned.append(stripped.lower())
    return cleaned


def encode_preferences(categories_csv: str, keywords_csv: str) -> str:
    # converting CSV in JSON BLOB for storing mysql
    # '{"categories": ["technology", "business"],
    # "keywords": ["tesla", "trump"]}'
    payload: Dict[str, List[str]] = {
        "categories": _split_csv(categories_csv),
        "keywords": _split_csv(keywords_csv),
    }
    return json.dumps(payload)


def decode_preferences(blob: str) -> Dict[str, List[str]]:
    # JSON decode with categories and keywords keys
    try:
        obj = json.loads(blob or "{}")
    except (json.JSONDecodeError, TypeError):
        obj = {}
    return {
        "categories": obj.get("categories", []),
        "keywords": obj.get("keywords", []),
    }
