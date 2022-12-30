from source.dbManager import DBManager
from flask_login import UserMixin
from passlib.hash import bcrypt
import os

class User(UserMixin):
    pass

class UserManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.pepper = os.getenv('PASSWORD_PEPPER')
        self.rounds = os.getenv('PASSWORD_ROUNDS')

    def find(self, username):
        if username is None:
            return None

        row = self.db_manager.one("SELECT username, password FROM user WHERE username = ?", params = (username,))
        
        try:
            username, password = row
        except:
            return None

        user = User()
        user.id = username
        user.password = password

        return user

    def validate(self, password, user):
        if user is None:
            return False

        password += self.pepper
        return bcrypt.verify(password, user.password)

    def add(self, username, password):

        password += self.pepper
        hash = bcrypt.using(rounds=self.rounds).hash(password)
        self.db_manager.execute("INSERT INTO user (username, password) VALUES (?, ?)", params = (username, hash))