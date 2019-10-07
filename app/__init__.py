from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from bs4 import BeautifulSoup
import hashlib
import sqlite3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# create and configure app
app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =('/index')
login_manager.refresh_view=('/index')
login_manager.session_protection = "strong"

limiter = Limiter(app, key_func=get_remote_address, default_limits=["20000/day", "500/hour"]) # set the maximum amout of tries before user get locked out for a time

Bootstrap(app)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

#Hash the password using SHA256 and a salt
def hash_password(user_password):
    SALT = '6385c57a230996dcbf7ba2bcb68b0b00'
    return hashlib.sha256(user_password.encode()+SALT.encode()).hexdigest()

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'], timeout=5000)
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

# TODO: Add more specific queries to simplify code

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

# Sanitize string, removes html
def sanitizeStr(value, strip = True):
    soup = BeautifulSoup(value,features="html.parser")
    text = soup.get_text(' ',strip=strip)
    return text

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@login_manager.user_loader
def load_user(user_id):
    try:
        with app.app_context():
            user = query_db('SELECT * FROM Users WHERE id=?', user_id )[0]
            return User(user['username'], user['password'], user['id'])
    except:
        return None

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
    os.mkdir(app.config['UPLOADED_PHOTOS_DEST'])

from app import routes, errors
