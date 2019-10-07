import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'V1p6H27sm]6eA`us!!r5&x"-,a['
    DATABASE = 'database.db'
    UPLOADED_PHOTOS_DEST = 'app/static/uploads'
    UPLOADED_PHOTOS_ALLOW = ('png', 'jpg', 'jpeg', 'gif')
    WTF_CSRF_ENABLED = True
    SESSION_PERMANENT=False
    REMEMBER_COOKIE_HTTPONLY = True