from flask import g, flash, abort, Flask, render_template, current_app, request, redirect, url_for
from datetime import datetime
from task import Task
from flask_login import login_user, login_required, current_user, logout_user
from users import get_user, User
from passlib.hash import pbkdf2_sha256 as hasher
from form import LoginForm, SignUpForm


def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)


def tasks_page():
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    return render_template("tasks.html", tasks=sorted(tasks))


@login_required
def task_page(url):
    print(url)
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    task = None
    for task_key, task in tasks:
        x_task = TaskManager.get_task(task_key)
        if x_task.url == url:
            task = x_task

    if task is None:
        abort(404)

    string = url + "_page"
    return redirect(url_for(string))
    # return render_template("task.html", task=task)


@login_required
def main_page():
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    return render_template("main.html", tasks=sorted(tasks))


@login_required
def task_add_page():
    if not (current_user.is_admin or current_user.is_coordi):
        abort(401)
    if request.method == "GET":
        return render_template(
            "task edit.html"
        )
    else:
        form_task = request.form["task"]
        form_url = request.form["url"]
        task = Task(form_task, url=int(form_url) if form_url else None)
        TaskManager = current_app.config["TaskManager"]
        TaskManager.add_task(task)
        return redirect(url_for("task_page", url=task.url))


def delete_task_page():
    if not current_user.is_admin:
        abort(403)
    TaskManager = current_app.config["TaskManager"]
    form_task_keys = request.form.getlist("task_keys")
    for form_task_key in form_task_keys:
        TaskManager.delete_task(int(form_task_key))
    tasks = TaskManager.get_tasks()

    return render_template("task-delete-page.html", tasks=sorted(tasks))


def edit_task_page():
    TaskManager = current_app.config["TaskManager"]
    if request.method == "GET":
        tasks = TaskManager.get_tasks()
        return render_template("task-edit-page.html", tasks=sorted(tasks))
    else:
        form_task_key = request.form["form_task_key"]
        task = TaskManager.get_task(form_task_key)

        return redirect(url_for('edit_task_page_master', task_key=form_task_key))


def edit_task_page_master(task_key):
    if request.method == "GET":
        TaskManager = current_app.config["TaskManager"]
        task = TaskManager.get_task(task_key)
        return render_template("task-edit-page-master.html", task=task
                               )
    else:
        TaskManager = current_app.config["TaskManager"]
        task = TaskManager.get_task(task_key)
        new_name = request.form["new_name"]
        new_url = request.form["new_url"]
        TaskManager.set_task(task_key, new_name, new_url)
        return redirect(url_for('task_page', url=task.url))


@login_required
def all_persons_page():
    if not (current_user.is_admin or current_user.is_coordi):
        abort(401)
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM person")
    persons = cursor.fetchall()
    title = "All employees"
    return render_template("tasks.html", persons=persons, title=title )


def signup_page():
    form = SignUpForm()
    if form.validate_on_submit():
        cursor = current_app.config["cursor"]
        password = request.form["password"]
        validpass = request.form["validpass"]
        cursor.execute("SELECT * FROM person WHERE mail=%(mail)s OR phone=%(phone)s", {'mail': request.form['mail'],
                                                                                       'phone': request.form['phone']})
        if not len(cursor.fetchall()) <= 0:
            flash("Already signed")
            return redirect(url_for('signup_page'))
        if validpass == password:
            password = hasher.hash(password)

            mydb = current_app.config["mydb"]
            if not len(str(request.form["phone"])) == 10:
                flash("geçerli bi telefon giriniz")
                return redirect(url_for('signup_page'))

            cursor.execute("SELECT MAX(pid) FROM person")

            max_pid = cursor.fetchone()['MAX(pid)']
            sql = "INSERT INTO person(pid,pass,first_name,second_name,phone,mail,score) " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val = (max_pid + 1, password, request.form["firstname"],
                   request.form["secondname"], request.form["phone"], request.form["mail"],0)
            cursor.execute(sql, val)
            mydb.commit()
            flash("Yeyyy you signed up")
            return redirect(url_for('login_page'))
        flash("pass is not same")
    if not current_user.is_authenticated:
        return render_template("signup.html", form=form)
    else:
        return redirect(url_for('main_page'))


def login_page():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    TaskManager = current_app.config["TaskManager"]
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form["username"]
        cursor = current_app.config["cursor"]
        cursor.execute("SELECT * FROM person WHERE mail=%(username)s or phone=%(username)s ", {'username': username})
        indexeduser = cursor.fetchall()
        user = None
        if not len(indexeduser) <= 0:
            user = get_user(indexeduser[0]['pid'])

        if user is not None:
            password = request.form["password"]
            if hasher.verify(password, user.password):

                login_user(user)

                # flash("Hoşgeldin" + user.username)
                next_page = request.args.get('next', url_for("main_page"))
                if user.is_admin:
                    TaskManager.add_task(Task("Add Events", "main"))
                    TaskManager.add_task(Task("All Employees", "all_persons"))

                    TaskManager.add_task(Task("My profile", "my_profile"))

                elif user.is_coordi:
                    TaskManager.add_task(Task("My Events", "my_events"))
                    TaskManager.add_task(Task("My Team", "my_team"))
                    TaskManager.add_task(Task("My profile", "my_profile"))

                return redirect(next_page)
        flash("Invalid credentials.")

    if not current_user.is_authenticated:
        return render_template("login.html", form=form)
    else:
        return redirect(url_for('main_page'))


def logout_page():
    logout_user()
    TaskManager = current_app.config["TaskManager"]
    TaskManager.clear_tasks()
    flash("You have logged out.")
    return redirect(url_for("main_page"))

@login_required
def my_profile_page():
    user_id = current_user.username
    return redirect(url_for('profile_page', user_id=user_id))

def profile_page(user_id):
    if not current_user.username == user_id:
        if not current_user.is_admin:
            abort(403)
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM PERSON WHERE pid=%(pid)s", {'pid': user_id})
    user = cursor.fetchall()[0]
    return render_template("profile.html", user=user)


@login_required
def update_profile_page(user_id):
    if not current_user.username == user_id:
        if not current_user.is_admin:
            abort(403)

    form = SignUpForm()
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM PERSON WHERE pid=%(pid)s", {'pid': user_id})
    user = cursor.fetchall()[0]
    if form.validate_on_submit():
        cursor.execute("SELECT * FROM person WHERE mail=%(mail)s OR phone=%(phone)s", {'mail': request.form['mail'],
                                                                                       'phone': request.form['phone']})
        temp = cursor.fetchall()
        if len(temp) > 1:
            flash("Already signed here")
            return redirect(url_for('update_profile_page',user_id=user_id))
        elif len(temp) == 1:
            if not user_id == temp[0]['pid']:
                flash("Already signed")
                return redirect(url_for('update_profile_page', user_id=user_id))

        password = request.form["password"]
        validpass = request.form["validpass"]
        if validpass == password and hasher.verify(password,user['pass']) or current_user.is_admin:
            cursor = current_app.config["cursor"]
            mydb = current_app.config["mydb"]
            if not len(str(request.form["phone"])) == 10:
                flash("geçerli bi telefon giriniz")
                return redirect(url_for('update_profile_page',user_id=user_id))

            sql = "UPDATE person SET first_name = %s, second_name= %s, mail=%s, phone=%s WHERE pid=%s"
            data = (request.form["firstname"],request.form["secondname"],request.form["mail"],request.form["phone"],user_id)
            cursor.execute(sql,data)
            mydb.commit()
            flash("Yeyyy you updated")
            return redirect(url_for('login_page'))
        flash("pass is not true")
    return render_template("signup.html", form=form, user=user)
