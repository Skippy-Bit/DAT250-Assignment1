import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'V1p6H27sm]6eA`us!!r5&x"-,a[' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    #UPLOAD_PATH = 'app/static/uploads'
    UPLOADED_PHOTOS_DEST = 'app/static/uploads'
    UPLOADED_PHOTOS_ALLOW = ('png', 'jpg', 'jpeg', 'gif')
    WTF_CSRF_ENABLED = True
    SESSION_PERMANENT=False
    #ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']  # Might use this at some point, probably don't want people to upload any file type
    REMEMBER_COOKIE_HTTPONLY = True
