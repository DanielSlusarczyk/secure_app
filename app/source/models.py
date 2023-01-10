from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
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
    TYPE_CHOICES = [('1', 'Private'), ('2', 'Private (Encrypted)'), ('3', 'Public')]

    type = SelectField(u'Type', choices=TYPE_CHOICES)

    submit = SubmitField('Save')