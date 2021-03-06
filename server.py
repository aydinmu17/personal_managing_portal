from flask import Flask, render_template, abort, session,redirect, url_for,current_app
from datetime import datetime
import view
from taskmanager import Tasks
from task import Task
from flask_login import UserMixin, LoginManager
from users import get_user
import mysql.connector
import os



login_manager = LoginManager()
app = Flask(__name__)
# mydb = mysql.connector.connect(
#     host= "localhost",
#     user="root",
#     password="",
#     database="emp"
# )

app.config["host"]="us-cdbr-east-03.cleardb.com"
app.config["user"]="b6e7b42e2aae67"
app.config["password"]="cb61c95e"
app.config["database"]="heroku_b87f3f2de9b268f"

mydb = mysql.connector.connect(
    host= app.config["host"],
    user=app.config["user"],
    password=app.config["password"],
    database=app.config["database"])

cursor = mydb.cursor(dictionary=True, buffered=True)


app.config["cursor"] = cursor
app.config["mydb"] = mydb
filepath = os.path.join(".", "init.sql")
sqlFile = open(filepath, "r").read()
cursor.execute(sqlFile,multi=True)



@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

app.add_url_rule("/login", view_func=view.login_page, methods=["GET", "POST"])
app.add_url_rule("/signup", view_func=view.signup_page, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=view.logout_page, methods=["GET", "POST"])
app.add_url_rule("/myProfile", view_func=view.my_profile_page,methods=["GET", "POST"])
app.add_url_rule("/profile/<int:user_id>", view_func=view.profile_page,methods=["GET", "POST"])
app.add_url_rule("/tasks/<url>", view_func=view.task_page)
app.add_url_rule("/update/<int:user_id>", view_func=view.update_profile_page, methods=["GET", "POST"])
app.add_url_rule("/", view_func=view.login_page, methods=["GET", "POST"])
app.add_url_rule("/main", view_func=view.main_page)
app.add_url_rule("/allpersons", view_func=view.all_persons_page)

app.add_url_rule("/evulation/<int:team_id>", view_func=view.evulation_page, methods=["GET", "POST"])


app.add_url_rule("/addProject", view_func=view.add_project, methods=["GET", "POST"])
app.add_url_rule("/project/<int:project_id>", view_func=view.project_page, methods=["GET", "POST"])
app.add_url_rule("/enrollProject", view_func=view.enroll_project_page, methods=["GET", "POST"])
app.add_url_rule("/enroll/<int:user_id>", view_func=view.enroll_project, methods=["GET", "POST"])
app.add_url_rule("/myProjects", view_func=view.my_projects_page, methods=["GET", "POST"])
app.add_url_rule("/updateProject/<int:project_id>", view_func=view.update_project_page, methods=["GET", "POST"])
app.add_url_rule("/deleteProject/<int:project_id>", view_func=view.delete_project, methods=["GET", "POST"])


app.add_url_rule("/addTeam", view_func=view.add_team_page, methods=["GET", "POST"])
app.add_url_rule("/myTeams", view_func=view.my_teams_page, methods=["GET", "POST"])
app.add_url_rule("/team/<int:team_id>", view_func=view.team_page, methods=["GET", "POST"])
app.add_url_rule("/editTeam/<int:team_id>", view_func=view.update_team_page, methods=["GET", "POST"])
app.add_url_rule("/assigntoTeamfromProject/<int:project_id>/<string:purpose>", view_func=view.assign_to_team_page, methods=["GET", "POST"])
app.add_url_rule("/deleteTeam/<int:team_id>", view_func=view.delete_team, methods=["GET", "POST"])



TaskManager = Tasks()
TaskManager.add_all_tasks()


app.config["TaskManager"] = TaskManager


login_manager.init_app(app)
login_manager.login_view = "login_page"

app.config.from_object("settings")

# def crate_app(app):
#     #Routes



if __name__ == "__main__":
    login_status = False
    # crate_app(app)
    app.run()
