import os, sqlite3

class DBManager:
    def __init__(self):
        self.database_path = os.getenv('DATABASE')
        self.init()

    def connect(self):
        self.db_connection = sqlite3.connect(self.database_path)

    def init(self):
        self.connect()
        sql_cursor = self.db_connection.cursor()

        sql_cursor.execute("DROP TABLE IF EXISTS user")
        sql_cursor.execute("DROP TABLE IF EXISTS notes")
        
        sql_cursor.execute("CREATE TABLE user (username VARCHAR(32), password VARCHAR(128))")
        sql_cursor.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, username VARCHAR(32), note VARCHAR(256))")
        self.db_connection.commit()
    
    def execute(self, sql, params=()):
        self.connect()
        sql_cursor = self.db_connection.cursor()
        sql_cursor.execute(sql, params)
        self.db_connection.commit()

    def one(self, sql, params=()):
        self.connect()
        sql_cursor = self.db_connection.cursor()
        sql_cursor.execute(sql, params)

        try:
            result = sql_cursor.fetchone()
        except:
            result = None

        return result

    def many(self, sql, params=()):
        self.connect()
        sql_cursor = self.db_connection.cursor()
        sql_cursor.execute(sql, params)
        
        try:
            result = sql_cursor.fetchall()
        except:
            result = None

        return result