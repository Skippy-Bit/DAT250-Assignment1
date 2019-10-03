
# models.py
from flask_login import UserMixin
from app import get_db

class User(UserMixin, get_db):
    id = get_db.Column(get_db.Integer, primary_key=True)
    username = get_db.Column(get_db.string(100), unique=True)
    password = get_db.Column(get_db.string(100))
