from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from source.dbManager import DBManager

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