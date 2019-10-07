from flask_login import UserMixin
# File containing all database models
class User(UserMixin):
    def __init__(self , username , password , id , active=True, authenticated=True):
        self.id = id
        self.username = username
        self.password = password
        self.active = active
        self.authenticated = authenticated

    def get_id(self):
        object_id = self.id
        return str(object_id)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active