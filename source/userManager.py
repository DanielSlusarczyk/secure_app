from password_strength import PasswordPolicy
from source.dbManager import DBManager
from flask_login import UserMixin
from passlib.hash import bcrypt
import os, string, math

class User(UserMixin):
    pass

class UserManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.pepper = os.getenv('PASSWORD_PEPPER')
        self.rounds = os.getenv('PASSWORD_ROUNDS')
        self.entrophy = os.getenv('PASSWORD_ENTROPHY')
        self.password_policy = PasswordPolicy.from_names(length = 8, uppercase = 2, numbers = 2)

    def find(self, username):
        if username is None:
            return None

        row = self.db_manager.one("SELECT id, username, password FROM user WHERE username = ?", params = (username,))
        
        try:
            id, username, password = row
        except:
            return None

        user = User()
        user.id = username
        user.db_id = id
        user.password = password
        return user

    def validate(self, password, user):
        if user is None:
            return False

        password += self.pepper
        return bcrypt.verify(password, user.password)

    def add(self, username, password):

        already_exists = self.db_manager.one("SELECT 1 FROM user WHERE username = ?", params = (username,))

        if already_exists:
            return "Username already exists!"

        if self.password_policy.test(password) != [] or not self.validate_strength(password):
            return "Password does not meet the security requirements!"

        password += self.pepper
        hash = bcrypt.using(rounds=self.rounds).hash(password)
        self.db_manager.execute("INSERT INTO user (username, password) VALUES (?, ?)", params = (username, hash))

    def validate_strength(self, password):

        lower, upper, digits, special, alphabet = False, False, False, False, 0

        for letter in password:
            if not lower and letter in string.ascii_lowercase:
                lower = True
                alphabet += len(string.ascii_lowercase)
            elif not upper and letter in string.ascii_uppercase:
                upper = True
                alphabet += len(string.ascii_uppercase)
            elif not digits and letter in string.digits:
                digits = True
                alphabet += len(string.digits)
            elif not special and letter in string.punctuation:
                special = True
                alphabet += len(string.punctuation)

        entrophy = len(password) * math.log(alphabet, 2)
        print(f"{password} -> {entrophy}")
        return entrophy > self.entrophy
