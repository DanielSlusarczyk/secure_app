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
        #sql_cursor.execute("DROP TABLE IF EXISTS logins")
        #
        #sql_cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, token TEXT, addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        #sql_cursor.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, owner TEXT, note TEXT, isPublic INTEGER, isEncrypted INTEGER, salt TEXT, tag TEXT, nonce TEXT, addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(owner) REFERENCES users(username))")
        #sql_cursor.execute("CREATE TABLE drafts (id INTEGER PRIMARY KEY, markdown TEXT, author TEXT, addDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(author) REFERENCES users(username))")
        #sql_cursor.execute("CREATE TABLE logins (id INTEGER PRIMARY KEY, user TEXT, host TEXT, attemp_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
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
        
        try:
            sql_cursor.execute(sql, params)
            result = sql_cursor.fetchone()
        except:
            result = None

        return result

    def many(self, sql, params=()):
        self.connect()
        sql_cursor = self.db_connection.cursor()
        
        try:
            sql_cursor.execute(sql, params)
            result = sql_cursor.fetchall()
        except:
            result = None

        return result