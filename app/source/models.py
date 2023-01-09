from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username", "autofocus": True})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Accept')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()], render_kw={"placeholder": "Username", "autofocus": True})

    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Password"})

    submit = SubmitField('Accept')

class KeyForm(FlaskForm):
    key = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Key"})

    submit = SubmitField('Accept')

class NoteForm(FlaskForm):
    markdown = TextAreaField()

    submit = SubmitField('View')

class MarkdownForm(FlaskForm):
    public = BooleanField('Public')
    encrypt = BooleanField('Encrypt')

    submit = SubmitField('Save')