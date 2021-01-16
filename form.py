from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SelectField
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


class EnrollProject(FlaskForm):
    project_id = StringField("project_id", validators=[DataRequired()])

class AddProject(FlaskForm):
    project_name = StringField("project_name", validators=[DataRequired()])
    manager_id = SelectField(u'manager name', choices=[])
    is_active = SelectField(u'is_active', choices=[(0,"No"),(1,"Yes")])

class AddTeam(FlaskForm):
    team_name = StringField("team_name", validators=[DataRequired()])
    leader_id = SelectField(u'leader_id', choices=[])
    project_id = SelectField(u'project_id', choices=[])




