from flask import current_app
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.firstname = 'first'
        self.active = True
        self.is_admin = False
        self.is_coordi = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(user_id):
    cursor = current_app.config["cursor"]
    cursor.execute("SELECT * FROM person WHERE pid=%(pid)s", {'pid': user_id})
    users = cursor.fetchall()
    # print(users)
    user = None
    if not len(users) <= 0:
        password = users[0]['pass']
        user = User(user_id, password) if password else None
        user.firstname = users[0]['first_name']

    if user is not None:
        user.is_admin = user.username in current_app.config["ADMIN_USERS"]
        if not user.is_admin:
            cursor.execute("SELECT * FROM TEAM WHERE leader_id=%(pid)s", {'pid': user_id})
            if not len(cursor.fetchall()) <= 0:
                user.is_coordi = True
    return user
