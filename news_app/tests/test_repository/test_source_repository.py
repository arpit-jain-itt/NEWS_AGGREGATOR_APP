import pytest
from unittest.mock import MagicMock, patch
from server.repository.source_repository import SourceRepository
from server.models.source_model import Source


@pytest.fixture
def repo():
    db = MagicMock()
    return SourceRepository(db)


def test_get_active_source(repo):
    source_row = {"id": 1, "name": "Test", "api_endpoint": "url", "api_key": "key"}
    source_instance = Source(**source_row)
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.return_value = source_row
    with patch.object(SourceRepository, "db", db, create=True), patch(
        "server.utils.repository_helper.row_to_model", return_value=source_instance
    ):
        repo = SourceRepository(db)
        result = repo.get_active_source()
        assert isinstance(result, Source)


def test_add_source(repo):
    with patch.object(SourceRepository, "add_source", return_value=True):
        repo = SourceRepository(MagicMock())
        assert repo.add_source("test") is True
