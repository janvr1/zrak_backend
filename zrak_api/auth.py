import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()

        if user is None:
            error = "Username does not exist"
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password"
        elif user['user_type'] != 1:
            error = "Inssuficient permissions"
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('manage.users_view'))

        flash(error)
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id, )).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view