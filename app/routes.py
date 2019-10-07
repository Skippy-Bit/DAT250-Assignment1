from flask import render_template, flash, redirect, url_for, request
from app import app, query_db, sanitizeStr, hash_password, User, photos
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from datetime import datetime
import os

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()

    if form.login.is_submitted() and form.login.submit.data and form.login.validate_on_submit():
        username = sanitizeStr(form.login.username.data)
        password = sanitizeStr(form.login.password.data)
        try:
            user = query_db('SELECT * FROM Users WHERE username=?',
                            form.login.username.data, one=True)
            if user == None:
                flash('Sorry, wrong username or password!')
            elif user['password']  ==  hash_password(form.login.password.data):
                login_user(User(user['username'], user['password'], user['id']), remember=form.login.remember_me.data)
                return redirect(url_for('stream', username=form.login.username.data))
            else:
                flash('Sorry, wrong username or password!')
        except Exception as e:
            flash('An error has occured, please contact the admin\nError was: {}'.format(e),'error')

    elif form.register.is_submitted() and form.register.submit.data and form.register.validate_on_submit():
        username = sanitizeStr(form.register.username.data)
        firstname = sanitizeStr(form.register.first_name.data)
        lastname = sanitizeStr(form.register.last_name.data)
        password = hash_password(sanitizeStr(form.register.password.data))
        flash('Congratulations, {} registered!'.format(sanitizeStr(form.register.username.data)))
        query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES(?, ?, ?, ?)', username, firstname,
                 lastname, password)
        return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
     if(current_user.username!=username):
        return redirect(url_for('stream', username=current_user.username))
     else:
        form = PostForm()
        user = query_db('SELECT * FROM Users WHERE username=?',
                        username, one=True)

        if form.is_submitted() and form.validate_on_submit():
            content = sanitizeStr(form.content.data, strip=False)

            if form.image.data:
                filename = photos.save(form.image.data)
            else:
                filename = None

            # if both content and image is blank.
            if form.content.data == '' and not form.image.data:
                return redirect(url_for('stream', username=current_user.username))

            query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?)',
                     user['id'], content, filename, datetime.now())
            return redirect(url_for('stream', username=current_user.username))

        posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) OR p.u_id=? ORDER BY p.creation_time DESC',
                         user['id'], user['id'], user['id'])
        return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)


# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    if(current_user.username!=username):
        return redirect(url_for('comments', username=current_user.username, p_id=p_id))
    else:
        form = CommentsForm()
        if form.is_submitted():
            comment = sanitizeStr(form.comment.data)
            # Dont post anything if form is empty
            if comment == '':
                return redirect(url_for('comments', username=current_user.username, p_id=p_id))

            user = query_db('SELECT * FROM Users WHERE username=?',
                            username, one=True)
            query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?)',
                     p_id, user['id'], comment, datetime.now())
            return redirect(url_for('comments', username=current_user.username, p_id=p_id)) # this clears the form after successfull post.

        post = query_db('SELECT * FROM Posts WHERE id=?', p_id, one=True)
        all_comments = query_db(
            'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id=? ORDER BY c.creation_time DESC', p_id)
        return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if(current_user.username!=username):
        return redirect(url_for('friends', username=current_user.username))
    else:
        form = FriendsForm()
        user = query_db('SELECT * FROM Users WHERE username=?',
                        username, one=True)
        if form.is_submitted():
            userSearch = sanitizeStr(form.username.data)
            friend = query_db(
                'SELECT * FROM Users WHERE username=?', userSearch, one=True)
            if friend is None:
                flash('User does not exist')
            else:
                query_db('INSERT INTO Friends (u_id, f_id) VALUES(?, ?)',
                         user['id'], friend['id'])

        all_friends = query_db(
            'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=?', user['id'], user['id'])
        return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        education = sanitizeStr(form.education.data)
        employment = sanitizeStr(form.employment.data)
        music = sanitizeStr(form.movie.data)
        movie = sanitizeStr(form.movie.data)
        nationality = sanitizeStr(form.nationality.data)
        birthday = form.birthday.data

        query_db('UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=?',
                 education, employment, music, movie, nationality, birthday, username)
        return redirect(url_for('profile', username=username))

    user = query_db('SELECT * FROM Users WHERE username=?',
                    username, one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have sucessfully logged out')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('stream', username=current_user.username))
