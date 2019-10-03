from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
#from flask_login import LoginManager
from bs4 import BeautifulSoup
import hashlib
import sqlite3
import os

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

# TODO: Handle login management better, maybe with flask_login?
#login = LoginManager(app)

#Hash the password using SHA256 and a salt
def hash_password(user_password):
    SALT = '6385c57a230996dcbf7ba2bcb68b0b00'
    return hashlib.sha256(user_password.encode()+SALT).hexdigest()

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

# TODO: Add more specific queries to simplify code


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

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes
