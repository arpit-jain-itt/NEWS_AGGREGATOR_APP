import pytest
from unittest.mock import patch, MagicMock
from server.repository.notification_repository import NotificationRepository


@pytest.fixture
def repo():
    db = MagicMock()
    return NotificationRepository(db)


def test_get_notifications_for_user(repo):
    with patch(
        "server.utils.repository_helper.rows_to_models", return_value=[MagicMock()]
    ):
        conn = repo.db.connect.return_value
        cursor = MagicMock()
        conn.close = MagicMock()
        with patch("server.utils.repository_helper.with_cursor", return_value=cursor):
            cursor.__enter__.return_value = cursor
            cursor.fetchall.return_value = [{}]
            result = repo.get_notifications_for_user(1)
            assert isinstance(result, list)


def test_create_or_update_notification_insert(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.close = MagicMock()
    cursor.fetchone.return_value = None
    cursor.lastrowid = 5
    with patch("server.utils.repository_helper.with_cursor", return_value=cursor):
        cursor.__enter__.return_value = cursor
        result = repo.create_or_update_notification(1, "kw")
        assert result == 5
