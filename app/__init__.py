from flask import Flask, g
import json
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
import sqlite3
import os

# create and configure app
app = Flask(__name__)
app.config.from_object(Config)
app.config['WTF_CSRF_ENABLED'] = True
# TODO: Handle login management better, maybe with flask_login?
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =('/index')

Bootstrap(app)

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, *args, **kwargs):
    db = get_db()
    one = kwargs.get('one', False)
    cursor = db.execute(query, (args))
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

def get_cursor():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('SELECT * FROM Users WHERE id=2')
        r = cur.fetchone()
        return r

class User(UserMixin):
    def __init__(self , username , password , id , active=True):
        self.id = id
        self.username = username
        self.password = password
        self.active = active

    def get_id(self):
        object_id = self.id
        return str(object_id)

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username , key='secret_key')

@login_manager.user_loader
def load_user(user_id):
    return User

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])


from app import routes
