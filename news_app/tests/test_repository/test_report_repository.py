import pytest
from unittest.mock import MagicMock, patch
from server.repository.report_repository import ReportRepository

@pytest.fixture
def repo():
    db = MagicMock()
    return ReportRepository(db)

def test_get_report_count(repo):
    # Success case
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.return_value = (3,)
    with patch.object(repo, 'db', db):
        result = repo.get_report_count(1)
        assert result == 3
    # Error case: fetchone returns empty tuple
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.return_value = ()
    with patch.object(repo, 'db', db):
        with pytest.raises(ValueError):
            repo.get_report_count(1)

def test_add_report(repo):
    with patch('server.utils.repository_helper.safe_execute', return_value=True):
        report = MagicMock()
        assert repo.add_report(report) is True

