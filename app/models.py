
# models.py
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.string(100), unique=True)
    password = db.Column(db.string(100))
