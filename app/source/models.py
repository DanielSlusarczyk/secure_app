from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, ValidationError
from wtforms.validators import InputRequired, Length
from source.userManager import UserManager
import string

user_manager = UserManager()

class RegisterForm(FlaskForm):
    username = StringField(
            validators=[
                InputRequired(message="Username should not be empty"), 
                Length(min=user_manager.min_length, max=user_manager.max_length, message="Username should be at least %(min)d and max %(max)d characters long")], 
            render_kw={"placeholder": "Username", "autofocus": True})

    password = PasswordField(
            validators=[
                InputRequired(message="Password shoud not be empty"), 
                Length(min=4, max=20, message="Password should be at least %(min)d and max %(max)d characters long")],
            render_kw={"placeholder": "Password"})

    submit = SubmitField('Accept')

    def validate_username(self, _):
        user_manager.validate_new_username(self.username.data)

    def validate_password(self, _):
        user_manager.validate_new_password(self.password.data)

class LoginForm(FlaskForm):
    username = StringField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Username", "autofocus": True})

    password = PasswordField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Password"})

    submit = SubmitField('Accept')

class KeyForm(FlaskForm):
    key = PasswordField(
            validators=[InputRequired()], 
            render_kw={"placeholder": "Key"})

    submit = SubmitField('Accept')

class NoteForm(FlaskForm):
    markdown = TextAreaField()

    submit = SubmitField('View')

class MarkdownForm(FlaskForm):
    TYPE_CHOICES = [('1', 'Private'), ('2', 'Private (Encrypted)'), ('3', 'Public')]

    type = SelectField(u'Type', choices=TYPE_CHOICES)

    submit = SubmitField('Save')