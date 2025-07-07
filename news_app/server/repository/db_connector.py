import mysql.connector
from mysql.connector import Error
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class DBConnector:
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=False,
                connection_timeout=3,
            )
            return connection
        except Error as e:
            print(f"Failed to connect to database: {e}")
            return None

    def close(self, connection):
        try:
            if connection and connection.is_connected():
                connection.close()
        except Exception:
            pass


db = DBConnector()
