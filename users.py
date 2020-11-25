from flask import current_app
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False
        self.is_coordi = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(user_id):
    password = current_app.config["PASSWORDS"].get(user_id)
    user = User(user_id, password) if password else None
    if user is not None:
        user.is_admin = user.username in current_app.config["ADMIN_USERS"]
        if not user.is_admin:
            user.is_coordi = user.username in current_app.config["COORDINATORS"]
    return user
