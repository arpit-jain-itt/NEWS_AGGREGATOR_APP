from datetime import datetime
from dataclasses import asdict


def get_pagination(args, default_limit=20):
    limit = int(args.get("limit", default_limit))
    if "offset" in args:
        offset = int(args.get("offset", 0))
    else:
        page = int(args.get("page", 1))
        offset = (page - 1) * limit
    return limit, offset


def require_fields(data, fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None


def safe_int(value, field_name="value"):
    try:
        return int(value), None
    except (ValueError, TypeError):
        return None, f"{field_name} must be an integer"


def require_header(request, header_name):
    value = request.headers.get(header_name)
    if not value:
        return None, f"{header_name} header is required"
    return value, None


def parse_iso_date(date_str, field_name="date"):
    try:
        return datetime.fromisoformat(date_str), None
    except (ValueError, TypeError):
        return None, f"Invalid {field_name}. Use YYYY-MM-DD."


def serialize_model(obj, extra_fields=None):
    d = asdict(obj)
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    if extra_fields:
        d.update(extra_fields)
    return d


def serialize_list(objs, extra_fields=None):
    return [serialize_model(obj, extra_fields) for obj in objs]


def make_response(data=None, message="", status_code=200, success=True):
    resp = {"success": success}
    if message:
        resp["message"] = message
    if data is not None:
        resp["data"] = data
    return resp, status_code
