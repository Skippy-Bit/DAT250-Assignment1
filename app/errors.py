from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from app import app

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Welcome'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Welcome'), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size to big!')
    return redirect(url_for('stream', username=current_user.username))
