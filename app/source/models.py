from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, ValidationError, EmailField
from wtforms.validators import InputRequired, Length, Email
from source.userManager import UserManager
import string

user_manager=UserManager()

class RegisterForm(FlaskForm):
    username=StringField(
            validators=[
                InputRequired(message="Username should not be empty"), 
                Length(min=user_manager.min_username, max=user_manager.max_username, message="Username should be at least %(min)d and max %(max)d characters long")], 
            render_kw={"placeholder": "Username", "autofocus": True})

    email=EmailField(
            validators=[
                InputRequired(message="E-mail should not be empaty"),
                Email(message="E-mail is invalid")],
                render_kw={"placeholder": "E-mail"})

    password=PasswordField(
            validators=[
                InputRequired(message="Password shoud not be empty"), 
                Length(min=user_manager.min_length, max=user_manager.max_length, message="Password should be at least %(min)d and max %(max)d characters long")],
            render_kw={"placeholder": "Password"})

    submit=SubmitField('Accept')

    def validate_username(self, _):
        user_manager.validate_new_username(self.username.data)

    def validate_password(self, _):
        user_manager.validate_new_password(self.password.data)

class LoginForm(FlaskForm):
    username=StringField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Username", "autofocus": True})

    password=PasswordField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Password"})

    submit=SubmitField('Accept')

class PasswordRecoveryForm(FlaskForm):
    username=StringField(
            validators=[
                InputRequired(message="Username should not be empty")], 
            render_kw={"placeholder": "Username", "autofocus": True})

    email=EmailField(
            validators=[
                InputRequired(message="E-mail should not be empaty"),
                Email(message="E-mail is invalid")],
                render_kw={"placeholder": "E-mail"})

    submit=SubmitField('Accept')
        
class PasswordRecoveryTokenForm(FlaskForm):
    token=StringField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Token"})

    new_password=PasswordField(
            validators=[
                InputRequired(message="Password shoud not be empty"), 
                Length(min=4, max=20, message="Password should be at least %(min)d and max %(max)d characters long")],
            render_kw={"placeholder": "New password"})

    def validate_new_password(self, _):
        user_manager.validate_new_password(self.new_password.data)

    submit=SubmitField('Accept')

class LockForm(FlaskForm):
    key=PasswordField(
            validators=[InputRequired(),
            Length(min=4, max=20, message="Key should be at least %(min)d and max %(max)d characters long")], 
            render_kw={"placeholder": "Key"})

    def validate_key(self, _):
        for letter in self.key.data:
            if letter in string.ascii_letters:
                continue
            if letter in string.digits:
                continue
            if letter in user_manager.allowed_signs:
                continue
            raise ValidationError(f"Character {letter} is not allowed")

    submit=SubmitField('Accept')

class UnlockForm(FlaskForm):
    key=PasswordField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Key"})

    submit=SubmitField('Accept')

class NoteForm(FlaskForm):
    markdown=TextAreaField()

    submit=SubmitField('View')

class LogoutForm(FlaskForm):
    logout=SubmitField('Log out')

class MarkdownForm(FlaskForm):
    TYPE_CHOICES=[('1', 'Private'), ('2', 'Private (Encrypted)'), ('3', 'Public')]

    type=SelectField('Type', choices=TYPE_CHOICES)

    def validate_type(self, _):
        user_type=self.type.data
        
        if user_type == 1:
            return
        if user_type == 2:
            return
        if user_type == 3:
            return
        
        raise ValidationError()

    submit=SubmitField('Save')