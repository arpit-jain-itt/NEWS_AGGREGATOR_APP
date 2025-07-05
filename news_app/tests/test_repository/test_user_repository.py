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

def test_get_user_by_email(repo):
    user_row = {'id': 1, 'username': 'u', 'email': 'e', 'password_hash': 'p'}
    user_instance = User(**user_row)
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.return_value = user_row
    with patch.object(UserRepository, 'db', db, create=True), \
         patch('server.utils.repository_helper.row_to_model', return_value=user_instance):
        repo = UserRepository(db)
        result = repo.get_user_by_email('e')
        assert isinstance(result, User)

def test_get_all_users(repo):
    with patch('server.utils.repository_helper.rows_to_models', return_value=[MagicMock()]):
        conn = repo.db.connect.return_value
        cursor = MagicMock()
        conn.close = MagicMock()
        with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
            cursor.__enter__.return_value = cursor
            cursor.fetchall.return_value = [{}]
            result = repo.get_all_users()
            assert isinstance(result, list)

def test_get_user_keywords_json(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = {"keywords": '["foo", "bar"]'}
        import json
        with patch('json.loads', return_value=["foo", "bar"]):
            result = repo.get_user_keywords(1)
            assert result == ["foo", "bar"]


