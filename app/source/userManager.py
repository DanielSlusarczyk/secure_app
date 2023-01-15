from password_strength import PasswordPolicy
from source.dbManager import DBManager
from wtforms import ValidationError
from flask_login import UserMixin
from passlib.hash import bcrypt
from uuid import uuid4
import os, string, math, time

class User(UserMixin):
    pass

class UserManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.pepper = os.getenv('PASSWORD_PEPPER')
        self.rounds = os.getenv('PASSWORD_ROUNDS')
        self.entrophy = int(os.getenv('PASSWORD_ENTROPHY'))
        self.min_length =  int(os.getenv('PASSWORD_MIN_LENGTH'))
        self.max_length = int(os.getenv('PASSWORD_MAX_LENGTH'))
        self.uppercase = int(os.getenv('PASSWORD_UPPERS'))
        self.numbers = int(os.getenv('PASSWORD_DIGITS'))
        self.allowed_signs = os.getenv('ALLOWED_SIGNS')

        self.min_username = int(os.getenv('USERNAME_MIN_LENGTH'))
        self.max_username = int(os.getenv('USERNAME_MAX_LENGTH'))

        self.waiting_time = int(os.getenv('WAITING_TIME_SEC'))

        self.password_policy = PasswordPolicy.from_names(
            length = self.min_length,
            uppercase = self.uppercase,
            numbers = self.numbers)

    def find(self, username):
        if username is None:
            return None

        try:
            (id, username, password) = self.db_manager.one('SELECT id, username, password FROM users WHERE username = ?', params = (username,))
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

        start_time = time.time()
        result = bcrypt.verify(password, user.password)
        hash_time = time.time() - start_time

        if hash_time < self.waiting_time:
            time.sleep(self.waiting_time - hash_time)

        return result

    def reach_limit(self, user, host):
        try:
            self.db_manager.execute('INSERT INTO logins (user, host) VALUES (?, ?)', params = (user, host))

            (attempts, ) = self.db_manager.one('SELECT COUNT() FROM logins WHERE host = ? AND attemp_time >= DATETIME(DATETIME(), "-5 minutes") ORDER BY attemp_time DESC', params = (host,))
        except:
            return 0

        return 1 if attempts >= 5 else 0

    def add(self, username, password, email):

        if (not username or not password or not email):
            return 'Some credential is empty'

        password += self.pepper
        hash = bcrypt.using(rounds=self.rounds).hash(password)
        self.db_manager.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', params = (username, hash, email))

    def generate_token(self, username, email):
        
        if (not username or not email):
            return
        
        token = str(uuid4())
        self.db_manager.execute('UPDATE users SET token = ? WHERE username = ? AND email = ?', params = (token, username, email))

        return token

    def set_password(self, username, email, token, new_pass):

        if (not username or not email or not token or not new_pass):
            return 'Credentials are invalid'
        
        correct_credential = self.db_manager.one('SELECT 1 FROM users WHERE username = ? AND email = ? AND token = ?', params = (username, email, token))

        if correct_credential is None:
            return 'Credentials are invalid'

        new_pass += self.pepper
        hash = bcrypt.using(rounds=self.rounds).hash(new_pass)
        self.db_manager.execute('UPDATE users SET password = ? WHERE username = ? AND email = ? AND token = ?', params = (hash, username, email, token))

    def find_logs(self, username):
        
        try:
            logs = self.db_manager.many('SELECT host, DATETIME(MAX(attemp_time), "localtime") AS last_login, COUNT(attemp_time) AS count FROM logins WHERE user = ? GROUP BY host LIMIT 5', params=(username, ))
            if logs is None:
                logs = []
        except:
            logs = []
            
        return logs


    def validate_new_username(self, username):

        self.validate_signs(username)

        already_exists = self.db_manager.one('SELECT 1 FROM users WHERE username = ?', params = (username,))
        if already_exists:
            raise ValidationError('Username already exists')

    def validate_recovery_data(self, username, email):

        already_exists = self.db_manager.one('SELECT 1 FROM users WHERE username = ? AND email = ?', params = (username, email))
        if already_exists is None:
            return 'Credentials are invalid'

    def validate_new_password(self, password):
        if self.password_policy.test(password) != []:
            raise ValidationError(f'Password should contain: {self.uppercase} uppercase, {self.numbers} numbers')
        
        self.validate_signs(password)

        self.validate_strength(password)

    def validate_signs(self, text):

        for letter in text:
            if letter in string.ascii_letters:
                continue
            if letter in string.digits:
                continue
            if letter in self.allowed_signs:
                continue

            raise ValidationError(f'Character {letter} is not allowed')

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
            elif not special and letter in self.allowed_signs:
                special = True
                alphabet += len(self.allowed_signs)

        entrophy = len(password) * math.log(alphabet, 2)

        if entrophy <= self.entrophy:
            raise ValidationError(f'Password is too weak. Use numbers, uppercase, lowercase and special signs')
