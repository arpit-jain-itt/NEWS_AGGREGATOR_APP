import pytest
from unittest.mock import MagicMock, patch
from server.repository.user_repository import UserRepository
from server.models.user_model import User


@pytest.fixture
def repo():
    db = MagicMock()
    return UserRepository(db)

def test_get_user_by_id(repo):
    user_row = {'id': 1, 'username': 'u', 'email': 'e', 'password_hash': 'p'}
    user_instance = User(**user_row)
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.return_value = user_row
    with patch.object(UserRepository, 'db', db, create=True), \
         patch('server.utils.repository_helper.row_to_model', return_value=user_instance):
        repo = UserRepository(db)
        result = repo.get_user_by_id(1)
        assert isinstance(result, User)

def test_create_user(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.close = MagicMock()
    cursor.lastrowid = 7
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        result = repo.create_user('u', 'e', 'p')
        assert result == 7 