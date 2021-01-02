from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Email
from wtforms_components import IntegerField

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])


class SignUpForm(FlaskForm):
    mail = StringField("mail", validators=[DataRequired(), Email()])
    phone = IntegerField("phone", validators=[DataRequired()])
    firstname = StringField("fistname", validators=[DataRequired()])
    secondname = StringField("secondname", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    validpass = PasswordField("validpass", validators=[DataRequired()])

