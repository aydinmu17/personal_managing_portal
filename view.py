from flask import g, flash, abort, Flask, render_template, current_app, request, redirect, url_for
from datetime import datetime
from task import Task
from flask_login import login_user, login_required, current_user, logout_user
from users import get_user, User
from passlib.hash import pbkdf2_sha256 as hasher
from form import *
import mysql.connector

def findManagerOfProject(project_id,projects):
    checkDBconnection()

    for project1 in projects:
        print(project1['pr_name'], project1['pr_id'], project_id)
        if int(project1['pr_id']) == int(project_id):
            return int(project1['manager_id'])

def addAvaragetoPeople(people):
    checkDBconnection()
    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    for person in people:
        cursor.execute("select * from team_with_members where pid=%(pid)s", {'pid': person['pid']})
        people_with_score = cursor.fetchall()
        scores = []
        if len(people_with_score) <= 0:
            avarage = 0
        else:
            for p in people_with_score:
                # print(p['score'])
                scores.append(p['score'])
                # print(scores)
            avarage = sum(scores) / len(scores)
            person['avarage_score'] = avarage
            cursor.execute("update person set score = %(score)s where pid = %(pid)s ",{'pid': person['pid'],'score':avarage})
            mydb.commit()

    return people


@login_required
def task_page(url):
    checkDBconnection()
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
    checkDBconnection()
    TaskManager = current_app.config["TaskManager"]




@login_required
def main_page():
    checkDBconnection()
    mydb=current_app.config['mydb']
    mydb.reconnect(attempts=1, delay=0)
    TaskManager = current_app.config["TaskManager"]
    tasks = TaskManager.get_tasks()
    if not tasks:
        TaskManager.add_all_tasks()
    return render_template("main.html", tasks=sorted(tasks))


@login_required
def all_persons_page():
    checkDBconnection()
    if not (current_user.is_admin or current_user.is_teamleader):
        abort(401)
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM person")
    people = cursor.fetchall()
    # for person in people:
    people=addAvaragetoPeople(people)
    #     cursor.execute("select * from team_with_members where pid=%(pid)s",{'pid': person['pid']} )
    #     people_with_score = cursor.fetchall()
    #     scores=[]
    #     if len(people_with_score)<=0:
    #         avarage=0
    #     else:
    #         for p in people_with_score:
    #             # print(p['score'])
    #             scores.append(p['score'])
    #             # print(scores)
    #         avarage = sum(scores) / len(scores)
    #         person['avarage_score'] = avarage
    #
    #     print(person)
    title = "All employees"
    return render_template("tasks.html", persons=people, title=title )


def signup_page():
    checkDBconnection()
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
            if max_pid is None:
                max_pid=0

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

    checkDBconnection()
    form = LoginForm()

    cursor = current_app.config["cursor"]

    if form.validate_on_submit():
        username = request.form["username"]
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



                return redirect(next_page)
        flash("Invalid credentials.")

    if not current_user.is_authenticated:
        return render_template("login.html", form=form)
    else:
        return redirect(url_for('main_page'))

@login_required
def logout_page():
    checkDBconnection()
    logout_user()

    flash("You have logged out.")
    return redirect(url_for("main_page"))

@login_required
def my_profile_page():
    checkDBconnection()
    user_id = current_user.username
    return redirect(url_for('profile_page', user_id=user_id))


@login_required
def profile_page(user_id):
    checkDBconnection()
    if not current_user.username == user_id:
        if not current_user.is_admin:
            abort(403)
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM PERSON WHERE pid=%(pid)s", {'pid': user_id})
    user = cursor.fetchall()[0]
    return render_template("profile.html", user=user)


@login_required
def update_profile_page(user_id):
    checkDBconnection()
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
    checkDBconnection()
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
    checkDBconnection()
    if not current_user.username == user_id:
        if not current_user.is_admin:
            if not current_user.is_teamleader:
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
    checkDBconnection()
    title= "My Projects"
    cursor = current_app.config["cursor"]
    if current_user.is_admin:
        cursor.execute("SELECT * FROM PROJECT inner JOIN Person on person.pid = project.manager_id order by is_active desc")
    else:
        cursor.execute("SELECT * FROM (ORGANIZATION"
                       " INNER JOIN PROJECT on organization.pr_id = project.pr_id "
                       "INNER JOIN PERSON ON PERSON.PID = PROJECT.MANAGER_ID) "
                       "where organization.pid=%(pid)s ORDER by is_active desc ",{'pid': current_user.username})

    list = cursor.fetchall()

    return render_template("list.html", title=title, list=list)

@login_required
def add_project():
    checkDBconnection()
    if not current_user.is_admin:
        abort(403)
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

        max_pr_id = cursor.fetchone()['MAX(pr_id)']
        if max_pr_id is None:
            max_pr_id = 0

        sql = "INSERT INTO project(pr_id,manager_id,pr_name,is_active) " \
              "VALUES (%s,%s,%s,%s)"
        val = (max_pr_id + 1, manager_id, project_name,1)
        cursor.execute(sql, val)
        mydb.commit()

        sql = "INSERT INTO organization(pid,pr_id) " \
              "VALUES (%s,%s)"
        val = (manager_id, max_pr_id+1)
        cursor.execute(sql, val)
        mydb.commit()

        flash(project_name + " added")
        return redirect(url_for("add_team_page"))

    return render_template("add project.html", form=form)

@login_required
def update_project_page(project_id):
    checkDBconnection()
    if not (current_user.is_admin or current_user.is_projectmanager):
        abort(403)

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

    if project['is_active']:
        form.is_active.choices.insert(0,(1,"Yes"))
        del form.is_active.choices[2]
    else:
        form.is_active.choices.insert(0,(0,"No"))
        del form.is_active.choices[1]

    if  request.method == 'POST':
        sql = "UPDATE project SET pr_name = %s, manager_id= %s, is_active=%s WHERE pr_id=%s"
        data = (
        request.form['project_name'],request.form['manager_id'], request.form['is_active'],project_id)
        cursor.execute(sql, data)
        mydb.commit()

        cursor.execute("UPDATE organization SET "
                       "pid=%(new_manager)s WHERE pr_id=%(pr_id)s and pid=%(old_manager)s",{'old_manager':manager.username, 'pr_id':project_id, 'new_manager':request.form['manager_id'] })
        mydb.commit()
        flash("Yeyyy you updated")
        return redirect(url_for('my_projects_page'))


    return render_template("add project.html",project=project,form=form)

@login_required
def delete_project(project_id):
    checkDBconnection()
    if not current_user.is_admin:
        abort(403)
    cursor= current_app.config["cursor"]
    mydb= current_app.config["mydb"]
    cursor.execute("select * from organization where pr_id = %(pr_id)s", {'pr_id': project_id})
    teams=cursor.fetchall()
    cursor.execute("select * from project where pr_id=%(pr_id)s", {'pr_id': project_id})
    project = cursor.fetchall()[0]
    cursor.execute("DELETE FROM PROJECT WHERE pr_id=%(pr_id)s", {'pr_id': project_id})
    cursor.execute("DELETE FROM ORGANIZATION WHERE pr_id=%(pr_id)s", {'pr_id': project_id})
    for team in teams:
        cursor.execute("DELETE FROM team_with_members WHERE t_id=%(t_id)s", {'t_id': team['t_id']})

    mydb.commit()
    flash(project['pr_name']+" removed")
    return redirect(url_for('my_projects_page'))

def project_page(project_id):
    checkDBconnection()
    cursor=current_app.config["cursor"]
    cursor.execute("select * from project "
                   "join person on project.manager_id=person.pid "
                   "where pr_id=%(pr_id)s", {'pr_id':project_id})
    project = cursor.fetchall()[0]
    cursor.execute("select * from team where pr_id=%(pr_id)s", {'pr_id':project_id})
    teams=cursor.fetchall()
    cursor.execute("select * from organization "
                   "join person on organization.pid=person.pid "
                   "where pr_id=%(pr_id)s and t_id is NULL", {'pr_id': project_id})
    people_without_team = cursor.fetchall()
    for peerson in people_without_team:
        if peerson['pid']==project['manager_id']:
            people_without_team.remove(peerson)

    cursor.execute("select * from "
                   "(organization join person on organization.pid=person.pid "
                   "join team on team.t_id=organization.t_id ) "
                   "where organization.pr_id=%(pr_id)s "
                   "order by organization.t_id and person.pid asc", {'pr_id':project_id})
    people_with_team = cursor.fetchall()

    people_without_team=addAvaragetoPeople(people_without_team)
    people_with_team = addAvaragetoPeople(people_with_team)

    return render_template("project.html",project=project,teams=teams,people_with_team=people_with_team,people_without_team=people_without_team)

def add_team_page():
    checkDBconnection()
    if not current_user.is_admin:
        if not current_user.is_projectmanager:
            abort(403)

    form = AddTeam()
    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    cursor.execute("SELECT * FROM PERSON")
    users = cursor.fetchall()
    form.leader_id.choices = [(user['pid'], user['first_name'] + " " + user['second_name']) for user in users]

    cursor.execute("SELECT * FROM project order by pr_id desc")
    projects = cursor.fetchall()
    form.project_id.choices = [(project['pr_id'], project['pr_name']) for project in projects]
    if request.method == 'POST':
        leader_id = request.form["leader_id"]
        team_name = request.form["team_name"]
        project_id = request.form["project_id"]

        manager_id_of_project = findManagerOfProject(project_id,projects)

        print(manager_id_of_project , current_user.username)
        if not current_user.is_admin:
            if manager_id_of_project != current_user.username:
                flash("Permission denied")
                return redirect(url_for('main_page'))

        cursor.execute("SELECT MAX(t_id) FROM team")

        max_t_id = cursor.fetchone()['MAX(t_id)']
        if max_t_id is None:
            max_t_id = 0
        sql = "INSERT INTO team(t_id,leader_id,pr_id,team_name) " \
              "VALUES (%s,%s,%s,%s)"
        val = (max_t_id + 1, leader_id, project_id, team_name)
        cursor.execute(sql, val)
        mydb.commit()
        sql = "INSERT INTO organization(pid,t_id,pr_id) " \
                  "VALUES (%s,%s,%s)"
        val = (leader_id,max_t_id+1,project_id)
        cursor.execute(sql,val)
        mydb.commit()

        sql = "INSERT INTO team_with_members(pid,t_id) " \
              "VALUES (%s,%s)"
        val = (leader_id, max_t_id+1)
        cursor.execute(sql, val)
        mydb.commit()

        flash(team_name + " added")
        return redirect(url_for("main_page"))
    return render_template("add_event.html",form=form)


@login_required
def update_team_page(team_id):
    checkDBconnection()
    if not current_user.is_admin:
        if not current_user.is_projectmanager:
            if not current_user.is_teamleader:
                abort(403)

    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]
    form=AddTeam()
    cursor.execute("SELECT * FROM team where t_id=%(t_id)s",{'t_id': team_id})
    team = cursor.fetchall()[0]
    cursor.execute("SELECT * FROM PERSON")
    users = cursor.fetchall()
    userlist = [(user['pid'],user['first_name']+" "+user['second_name']) for user in users]
    leader = get_user(team['leader_id'])
    form.leader_id.choices = [(leader.username, leader.firstname+" "+leader.secondname)] + userlist

    cursor.execute("SELECT * FROM project")
    projects = cursor.fetchall()
    projectlist = [(project['pr_id'], project['pr_name']) for project in projects]
    cursor.execute("Select * from project where pr_id=%(pr_id)s",{'pr_id':team['pr_id']})
    project = cursor.fetchall()[0]
    form.project_id.choices = [(project['pr_id'], project['pr_name'])]+projectlist

    if  request.method == 'POST':
        sql = "UPDATE team SET team_name = %s, leader_id= %s, pr_id=%s WHERE t_id=%s"
        data = (
        request.form['team_name'],request.form['leader_id'], request.form['project_id'],team_id)
        cursor.execute(sql, data)
        mydb.commit()
        flash("Yeyyy you updated")
        return redirect(url_for('main_page'))


    return render_template("add_event.html",team=team,form=form)
@login_required
def assign_to_team_page(project_id,purpose):
    checkDBconnection()

    cursor=current_app.config["cursor"]
    mydb=current_app.config["mydb"]
    cursor.execute("select * from project where pr_id=%(pr_id)s",{'pr_id':project_id})
    project = cursor.fetchall()[0]
    if not (current_user.is_admin or current_user.username==project['manager_id']):
        abort(403)

    if purpose == "assign":
        title = "Assign Member"
        cursor.execute(
            "select * from organization join person on organization.pid=person.pid where pr_id=%(pr_id)s and t_id is NULL",
            {'pr_id': project_id})
        people = cursor.fetchall()
        for peerson in people:
            if peerson['pid'] == project['manager_id']:
                people.remove(peerson)
    else:
        if purpose == 'updateMember':
            title = "Update Member"
        else:
            title = "Take Out Member"

        cursor.execute(
            "select * from organization join person on organization.pid=person.pid where pr_id=%(pr_id)s and t_id is not NULL",
            {'pr_id': project_id})
        people = cursor.fetchall()
    cursor.execute("select * from team where pr_id=%(pr_id)s",{'pr_id':project_id})
    teams=cursor.fetchall()
    if request.method == 'POST':
        user_ids=request.form.getlist("user_id")
        if purpose == "assign":
            team_id = request.form["team"]

            for user_id in user_ids:
                sql = "UPDATE organization SET t_id=%s WHERE pid=%s and pr_id=%s"
                data = (team_id,user_id,project_id)
                cursor.execute(sql,data)
                mydb.commit()

                sql = "INSERT INTO team_with_members(pid,t_id) " \
                      "VALUES (%s,%s)"
                val = (user_id,team_id)
                cursor.execute(sql, val)
                mydb.commit()

            flash("users has assigned")
            return redirect(url_for('project_page',project_id=project_id))
        elif purpose == "takeOutfromTeam":
            for user_id in user_ids:
                cursor.execute("select * from organization where pid=%(pid)s and pr_id=%(pr_id)s ",{'pid':user_id,'pr_id':project_id})
                sql = "UPDATE organization SET t_id = NULL WHERE pid=%s and pr_id=%s"
                data = (user_id, project_id)
                cursor.execute(sql, data)
                mydb.commit()
                cursor.execute("select * from team where pr_id = %(pr_id)s",{'pr_id':project_id})
                teamIDs = cursor.fetchall()
                for old_team in teamIDs:
                    sql = "delete from team_with_members WHERE pid=%s and t_id=%s"
                    data = (user_id, old_team['t_id'])
                    cursor.execute(sql, data)
                    mydb.commit()

            flash("users removed")

            return redirect(url_for('project_page', project_id=project_id))
        elif purpose == "updateMember":
            team_id = request.form["team"]
            for user_id in user_ids:
                cursor.execute("select * from organization where pid=%(pid)s and pr_id=%(pr_id)s ",{'pid':user_id,'pr_id':project_id})
                old_team=cursor.fetchall()[0]['t_id']
                sql = "UPDATE organization SET t_id = %s WHERE pid=%s and pr_id=%s"
                data = (team_id,user_id, project_id)
                cursor.execute(sql, data)
                mydb.commit()
                sql = "update team_with_members set t_id=%s where pid=%s and t_id=%s"
                print(team_id,user_id,old_team)
                data = (team_id,user_id, old_team)
                cursor.execute(sql, data)
                mydb.commit()
            flash("users updated")
            return redirect(url_for('project_page', project_id=project_id))


    return render_template("assign_to_team.html", title =title,persons=people,teams=teams,purpose=purpose)

def my_teams_page():
    checkDBconnection()
    title = "My Teams"
    cursor = current_app.config["cursor"]
    list=[]
    if current_user.is_admin:
        cursor.execute(
            "SELECT team.t_id,leader_id,manager_id,team.pr_id,first_name , second_name, team_name,pr_name "
            "FROM TEAM "
            "inner JOIN Person on person.pid = team.leader_id "
            "inner join project on team.pr_id = project.pr_id")
        list = cursor.fetchall()
    else:
        cursor.execute("SELECT team.t_id,leader_id,manager_id,team.pr_id,first_name , second_name, team_name,pr_name "
                       "FROM team_with_members "
                       "inner join team on team_with_members.t_id = team.t_id "
                       "inner JOIN Person on person.pid = team.leader_id "
                       "inner join project on project.pr_id = team.pr_id "
                       "where team_with_members.pid=%(pid)s",{'pid':current_user.username})
        list = cursor.fetchall()
        if current_user.is_projectmanager:
            cursor.execute("select * from project where manager_id = %(manager_id)s ",{'manager_id': current_user.username})
            projects = cursor.fetchall()
            teamsFromproject=[]
            for project in projects:
                project_id = project['pr_id']
                cursor.execute(
                    "select team.t_id,leader_id,manager_id,team.pr_id,first_name,second_name,team_name,pr_name from organization "
                    "inner join team on team.t_id = organization.t_id "
                    "inner join project on project.pr_id = team.pr_id "
                    "inner join person on person.pid = team.leader_id "
                    "where project.pr_id=%(pr_id)s", {'pr_id': project_id})
                teamsFromproject = teamsFromproject + cursor.fetchall()
            for team in teamsFromproject:
                if not team in list:
                    list.append(team)
            print("is pm")
            print(list)


    print(list)

    return render_template("list2.html", title=title, list=list)

def team_page(team_id):
    checkDBconnection()
    cursor=current_app.config["cursor"]
    cursor.execute("select * from team "
                   "inner join person on team.leader_id=person.pid "
                   "inner join project on team.pr_id = project.pr_id "
                   "where team.t_id=%(t_id)s", {'t_id':team_id})
    team = cursor.fetchall()[0]
    team['t_id']=team_id
    cursor.execute("select * from team_with_members "
                   "inner join person on team_with_members.pid = person.pid "
                   "where t_id=%(t_id)s ",{'t_id': team_id})
    members = cursor.fetchall()
    sum = 0
    counter = 0
    for person in members:
        counter = counter + 1
        sum = sum + person['score']
    team['avarage_score'] = sum / counter


    return render_template("team.html",team=team,members=members)

@login_required
def delete_team(team_id):

    checkDBconnection()
    cursor=current_app.config["cursor"]
    mydb=current_app.config["mydb"]
    cursor.execute("select * from organization "
                   "inner join project on organization.pr_id = project.pr_id "
                   "inner join team on organization.pr_id = team.pr_id "
                   "where team.t_id = %(t_id)s",{'t_id': team_id})
    team = cursor.fetchall()[0]
    project_id=team['pr_id']
    project_manager_id = team['manager_id']
    if not (current_user.is_admin or current_user.username == project_manager_id):
        abort(403)

    cursor.execute("delete from team_with_members "
                   "where t_id = %(t_id)s",{'t_id': team_id})
    mydb.commit()
    cursor.execute("delete from organization "
                   "where t_id = %(t_id)s",{'t_id': team_id})
    mydb.commit()
    cursor.execute("delete from team "
                   "where t_id = %(t_id)s",{'t_id': team_id})
    mydb.commit()
    flash(team['team_name'] + " team deleted")
    return redirect(url_for('project_page',project_id=project_id))


def evulation_page(team_id):
    checkDBconnection()
    cursor = current_app.config["cursor"]
    mydb = current_app.config["mydb"]

    cursor.execute("select first_name, second_name,person.pid,team_with_members.score,comments from team_with_members join person on team_with_members.pid = person.pid where t_id = %(t_id)s",{'t_id':team_id})
    members = cursor.fetchall()
    cursor.execute("select * from team where t_id=%(t_id)s",{'t_id':team_id})
    team = cursor.fetchall()[0]

    if request.method == "POST":
        index = 0
        scores = request.form.getlist('score')
        commits =request.form.getlist('textarea')
        for member in members:
            print(member['score'])
            cursor.execute("update team_with_members set score = %(score)s , comments= %(commits)s where pid = %(pid)s",{'score': scores[index],'commits':commits[index],'pid':member['pid']})
            mydb.commit()
            index = index +1
        addAvaragetoPeople(members)
        flash("updated")
        return redirect(url_for('evulation_page',team_id=team_id))

    return render_template("evulation.html", persons = members,team=team)

