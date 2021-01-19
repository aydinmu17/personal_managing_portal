from flask import current_app
from flask_login import UserMixin
from form import checkDBconnection


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.firstname = 'first'
        self.secondname = 'second'
        self.active = True
        self.is_admin = False
        self.is_teamleader = False
        self.is_projectmanager = False
        self.role = "employee"

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(user_id):
    checkDBconnection()
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM person WHERE pid=%(pid)s", {'pid': user_id})
    users = cursor.fetchall()
    # print(users)
    user = None
    if not len(users) <= 0:
        password = users[0]['pass']
        user = User(user_id, password) if password else None
        user.firstname = users[0]['first_name']
        user.secondname = users[0]['second_name']

    if user is not None:
        cursor.execute("SELECT * FROM person WHERE pid=%(pid)s", {'pid': user_id})
        dbuser=cursor.fetchall()[0]
        if not len(dbuser) <= 0:
            if dbuser['mail']=="admin@admin.com":
                user.is_admin = True
                user.role="admin"

        if not user.is_admin:
            cursor.execute("SELECT * FROM TEAM WHERE leader_id=%(pid)s", {'pid': user_id})
            if not len(cursor.fetchall()) <= 0:
                user.is_teamleader = True
                user.role="team_leader"

            cursor.execute("SELECT * FROM project WHERE manager_id=%(pid)s", {'pid': user_id})
            if not len(cursor.fetchall()) <= 0:
                user.is_projectmanager = True
                user.role="project_manager"

    return user
