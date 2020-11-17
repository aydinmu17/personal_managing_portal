from flask import abort, Flask, render_template, current_app,request, redirect, url_for
from datetime import datetime
from task import Task


def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)


def tasks_page():
    db = current_app.config["db"]
    tasks = db.get_tasks()
    return render_template("tasks.html", tasks=sorted(tasks))


def task_page(task_key):
    db = current_app.config["db"]
    task = db.get_task(task_key)
    if task is None:
        abort(404)
    return render_template("task.html", task=task)


def main_page():
    db = current_app.config["db"]
    tasks = db.get_tasks()
    return render_template("main.html", tasks=sorted(tasks))


def task_add_page():
    if request.method == "GET":
        return render_template(
            "task edit.html", url_min=19, url_max=203
        )
    else:
        form_task = request.form["task"]
        form_url = request.form["url"]
        task = Task(form_task, url=int(form_url) if form_url else None)
        db = current_app.config["db"]
        task_key = db.add_task(task)
        return redirect(url_for("task_page", task_key=task_key))


def delete_task_page():
    db = current_app.config["db"]
    form_task_keys = request.form.getlist("task_keys")
    for form_task_key in form_task_keys:
        db.delete_task(int(form_task_key))
    tasks = db.get_tasks()

    return render_template("task-delete-page.html", tasks=sorted(tasks))


def edit_task_page():
    db = current_app.config["db"]
    if request.method == "GET":
        tasks = db.get_tasks()
        return render_template("task-edit-page.html", tasks=sorted(tasks))
    else:
        form_task_key = request.form["form_task_key"]
        task = db.get_task(form_task_key)

        return redirect(url_for('edit_task_page_master', task_key=form_task_key))


def edit_task_page_master(task_key):
    if request.method == "GET":
        db = current_app.config["db"]
        task = db.get_task(task_key)
        return render_template("task-edit-page-master.html", task=task
                                )
    else:
        db = current_app.config["db"]
        task = db.get_task(task_key)
        new_name = request.form["new_name"]
        new_url = request.form["new_url"]
        db.set_task(task_key, new_name, new_url)
        return redirect(url_for('task_page', task_key=task_key))


