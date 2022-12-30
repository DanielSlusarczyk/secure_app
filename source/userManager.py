from source.dbManager import DBManager
from flask_login import UserMixin
from passlib.hash import sha256_crypt

class User(UserMixin):
    pass

class UserManager:
    def __init__(self):
        self.db_manager = DBManager()

    def validate(self, username):
        if username is None:
            return None

        row = self.db_manager.one(f"SELECT username, password FROM user WHERE username = '{username}'")
        
        try:
            username, password = row
        except:
            return None

        user = User()
        user.id = username
        user.password = password

        return user

    def add(self, username, password):

        self.db_manager.execute(f"INSERT INTO user (username, password) VALUES ('{username}', '{sha256_crypt.hash(password)}')")