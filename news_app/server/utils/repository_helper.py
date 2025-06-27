from typing import Any, Callable, List, Optional, Type, Dict
from contextlib import contextmanager


@contextmanager
def with_cursor(conn, dictionary=False, buffered=False):
    cursor = conn.cursor(dictionary=dictionary, buffered=buffered)
    try:
        yield cursor
    finally:
        cursor.close()


def safe_execute(func: Callable, *args, default=None, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        return default


def rows_to_models(rows: List[Dict], model_cls: Type) -> List[Any]:
    return [model_cls(**row) for row in rows] if rows else []


def row_to_model(row: Optional[Dict], model_cls: Type) -> Optional[Any]:
    return model_cls(**row) if row else None


def optional_return(value, default=None):
    return value if value is not None else default


def commit_or_rollback(conn, func: Callable, *args, **kwargs):
    try:
        func(*args, **kwargs)
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False


def bulk_insert(conn, query: str, values: List[tuple]):
    with conn.cursor() as cursor:
        cursor.executemany(query, values)
    conn.commit()


def fetch_one(conn, query: str, params: tuple = (), dictionary=False, buffered=False):
    with with_cursor(conn, dictionary=dictionary, buffered=buffered) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def fetch_all(conn, query: str, params: tuple = (), dictionary=False, buffered=False):
    with with_cursor(conn, dictionary=dictionary, buffered=buffered) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
