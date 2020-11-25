from flask import Flask, render_template, abort, session
from datetime import datetime
import view
from database import Database
from task import Task
from flask_login import UserMixin, LoginManager
from users import get_user

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


def crate_app():
    app = Flask(__name__)
    app.add_url_rule("/login", view_func=view.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=view.logout_page, methods=["GET", "POST"])
    app.add_url_rule("/tasks", view_func=view.tasks_page)
    app.add_url_rule("/tasks/<int:task_key>", view_func=view.task_page)
    app.add_url_rule("/", view_func=view.main_page)
    app.add_url_rule("/new-task", view_func=view.task_add_page, methods=["GET", "POST"])
    app.add_url_rule("/task-delete", view_func=view.delete_task_page, methods=["GET", "POST"])
    app.add_url_rule("/task-edit", view_func=view.edit_task_page, methods=["GET", "POST"])
    app.add_url_rule("/task-edit/<int:task_key>", view_func=view.edit_task_page_master, methods=["GET", "POST"])

    db = Database()
    for x in range(1, 11):
        db.add_task(Task("Task " + str(x), url="task_" + str(x)))

    db.add_task(Task("Bu bir tasktir ", url="task_" + str(x)))
    app.config["db"] = db

    login_manager.init_app(app)
    login_manager.login_view = "login_page"

    app.config.from_object("settings")
    return app


if __name__ == "__main__":
    app = crate_app()
    app.run(host="0.0.0.0", port=8080)
