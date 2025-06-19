import mysql.connector
from mysql.connector import Error
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class DBConnector:
    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
                )
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                raise e
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None


db = DBConnector()
