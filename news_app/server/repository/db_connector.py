import mysql.connector
from mysql.connector import Error
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from server.utils.repository_helper import safe_execute


class DBConnector:
    def __init__(self):
        self.connection = None

    def connect(self):
        def do_connect():
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
                )
            return self.connection

        return safe_execute(do_connect)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None


db = DBConnector()
