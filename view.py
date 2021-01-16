from flask import g, flash, abort, Flask, render_template, current_app, request, redirect, url_for
from datetime import datetime
from task import Task
from flask_login import login_user, login_required, current_user, logout_user
from users import get_user, User
from passlib.hash import pbkdf2_sha256 as hasher
from form import *


@login_required
def tasks_page():
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    return render_template("tasks.html", tasks=sorted(tasks))

@login_required
def task_page(url):
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

def define_tasks(user):
    TaskManager = current_app.config["TaskManager"]
    if user.is_admin:
        TaskManager.add_task(Task("Add Events", "main"))
        TaskManager.add_task(Task("All Employees", "all_persons"))
        TaskManager.add_task(Task("My profile", "my_profile"))
        TaskManager.add_task(Task("Enroll Project", "enroll_project"))
        TaskManager.add_task(Task("Projects", "my_projects"))


    elif user.is_coordi:
        TaskManager.add_task(Task("My projects", "my_projects"))
        TaskManager.add_task(Task("My Team", "my_team"))
        TaskManager.add_task(Task("Enroll Project", "enroll_project"))

        TaskManager.add_task(Task("My profile", "my_profile"))
    else:
        TaskManager.add_task(Task("Enroll Project", "enroll_project"))
        TaskManager.add_task(Task("My profile", "my_profile"))
        TaskManager.add_task(Task("My projects", "my_projects"))

@login_required
def main_page():
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    if not tasks:
        define_tasks(current_user)

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

@login_required
def delete_task_page():
    if not current_user.is_admin:
        abort(403)
    TaskManager = current_app.config["TaskManager"]
    form_task_keys = request.form.getlist("task_keys")
    for form_task_key in form_task_keys:
        TaskManager.delete_task(int(form_task_key))
    tasks = TaskManager.get_tasks()

    return render_template("task-delete-page.html", tasks=sorted(tasks))

@login_required
def edit_task_page():
    TaskManager = current_app.config["TaskManager"]
    if request.method == "GET":
        tasks = TaskManager.get_tasks()
        return render_template("task-edit-page.html", tasks=sorted(tasks))
    else:
        form_task_key = request.form["form_task_key"]
        task = TaskManager.get_task(form_task_key)

        return redirect(url_for('edit_task_page_master', task_key=form_task_key))

@login_required
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
                define_tasks(user)



                return redirect(next_page)
        flash("Invalid credentials.")

    if not current_user.is_authenticated:
        return render_template("login.html", form=form)
    else:
        return redirect(url_for('main_page'))

@login_required
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

@login_required
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

@login_required
def enroll_project_page():
    user_id = current_user.username
    if current_user.is_admin:
        if request.method == "GET":
            cursor = current_app.config["cursor"]
            cursor.execute("SELECT * FROM person")
            persons = cursor.fetchall()
            title = "Select Employee"
            return render_template("tasks.html", persons=persons, title=title)
        else:
            user_id = request.form["user_id"]
            return redirect(url_for('enroll_project', user_id=user_id))
    return redirect(url_for('enroll_project', user_id=user_id))


@login_required
def enroll_project(user_id):
    if not current_user.username == user_id:
        if not current_user.is_admin:
            if not current_user.is_coordi:
                abort(403)

    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    form = EnrollProject()
    cursor.execute("SELECT * FROM PERSON WHERE pid=%(pid)s", {'pid': user_id})
    user = cursor.fetchall()[0]
    cursor.execute("SELECT * FROM PROJECT WHERE is_active=1")
    active_projects = cursor.fetchall()
    if form.validate_on_submit():
        project_id = request.form["project_id"]
        cursor.execute("SELECT * FROM organization WHERE pid=%(pid)s and pr_id=%(pr_id)s", {'pid': user_id, 'pr_id' : project_id})
        control = cursor.fetchall()
        if len(control) > 0:
            flash("You have already enrolled")
            return render_template("enroll_project.html", form=form, user=user, active_projects=active_projects)

        sql = "INSERT INTO organization(pid,pr_id) " \
              "VALUES (%s,%s)"
        val = (user_id,project_id)
        cursor.execute(sql, val)
        mydb.commit()
        flash("You have enrolled")
        return redirect(url_for("main_page"))

    return render_template("enroll_project.html", form=form,user=user,active_projects=active_projects)


@login_required
def my_projects_page():
    title= "My Projects"
    cursor = current_app.config["cursor"]
    if current_user.is_admin:
        cursor.execute("SELECT * FROM PROJECT inner JOIN Person on person.pid = project.manager_id order by is_active desc")
    else:
        cursor.execute("SELECT * FROM ORGANIZATION JOIN PROJECT on organization.pr_id = project.pr_id where pid=%(pid)s order by is_active desc",{'pid': current_user.username})

    list = cursor.fetchall()

    return render_template("list.html", title=title, list=list)


def add_project():
    form = AddProject()
    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    cursor.execute("SELECT * FROM PERSON")
    users = cursor.fetchall()
    form.manager_id.choices = [(user['pid'],user['first_name']+" "+user['second_name']) for user in users]
    if request.method == 'POST':
        manager_id = request.form["manager_id"]
        project_name = request.form["project_name"]

        cursor.execute("SELECT MAX(pr_id) FROM project")

        max_pid = cursor.fetchone()['MAX(pr_id)']
        sql = "INSERT INTO project(pr_id,manager_id,pr_name,is_active) " \
              "VALUES (%s,%s,%s,%s)"
        val = (max_pid + 1, manager_id, project_name,1)
        cursor.execute(sql, val)
        mydb.commit()
        flash(project_name + " added")
        return redirect(url_for("my_projects_page"))

    return render_template("add project.html", form=form)


def update_project_page(project_id):
    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    form=AddProject()
    cursor.execute("SELECT * FROM project where pr_id=%(pr_id)s",{'pr_id': project_id})
    project=cursor.fetchall()[0]
    cursor.execute("SELECT * FROM PERSON")
    users = cursor.fetchall()
    userlist = [(user['pid'],user['first_name']+" "+user['second_name']) for user in users]
    manager = get_user(project['manager_id'])
    form.manager_id.choices = [(manager.username, manager.firstname+" "+manager.secondname)] + userlist

    if  request.method == 'POST':
        sql = "UPDATE project SET pr_name = %s, manager_id= %s, is_active=%s WHERE pr_id=%s"
        data = (
        request.form['project_name'],request.form['manager_id'], request.form['is_active'],project_id)
        cursor.execute(sql, data)
        mydb.commit()
        flash("Yeyyy you updated")
        return redirect(url_for('my_projects_page'))


    return render_template("add project.html",project=project,form=form)

def delete_project(project_id):
    cursor= current_app.config["cursor"]
    mydb= current_app.config["mydb"]
    cursor.execute("select * from project where pr_id=%(pr_id)s", {'pr_id': project_id})
    project = cursor.fetchall()[0]
    cursor.execute("DELETE FROM PROJECT WHERE pr_id=%(pr_id)s", {'pr_id': project_id})
    cursor.execute("DELETE FROM ORGANIZATION WHERE pr_id=%(pr_id)s", {'pr_id': project_id})
    mydb.commit()
    flash(project['pr_name']+" removed")
    return redirect(url_for('my_projects_page'))


