import pytest
from unittest.mock import patch, MagicMock
from server.repository import db_connector
from server.repository.db_connector import DBConnector

def test_connect_success():
    with patch('mysql.connector.connect', return_value=MagicMock()):
        db = DBConnector()
        conn = db.connect()
        assert conn is not None

def test_connect_failure():
    with patch('mysql.connector.connect', side_effect=Exception()):
        db = DBConnector()
        with pytest.raises(Exception):
            db.connect() 