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

        #sql_cursor.execute("DROP TABLE IF EXISTS users")
        #sql_cursor.execute("DROP TABLE IF EXISTS notes")
        #sql_cursor.execute("DROP TABLE IF EXISTS drafts")
        
        #sql_cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(32), password VARCHAR(128), addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        #sql_cursor.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, owner VARCHAR(32), note VARCHAR(500), isPublic INTEGER, isEncrypted INTEGER, salt VARCHAR(20), tag VARCHAR(20), nonce VARCHAR(20), addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(owner) REFERENCES users(username))")
        #sql_cursor.execute("CREATE TABLE drafts (id INTEGER PRIMARY KEY, markdown VARCHAR(500), author VARCHAR(32), addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(author) REFERENCES users(username))")
        self.db_connection.commit()
    
    def execute(self, sql, params=()):
        self.insert(sql, params)

    def insert(self, sql, params=()):
        self.connect()
        sql_cursor = self.db_connection.cursor()
        sql_cursor.execute(sql, params)
        self.db_connection.commit()
        return sql_cursor.lastrowid

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