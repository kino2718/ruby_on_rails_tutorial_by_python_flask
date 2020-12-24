from flask import (Blueprint, render_template, session, request, abort,
                   redirect, url_for, flash)
import secrets
from ..models.user import User
from ..helpers.application_helper import csrf_token, check_csrf_token
from ..helpers.sessions_helper import log_in, log_out

bp = Blueprint('sessions', __name__, url_prefix='')

_CSRF_TOKEN= 'csrf_token'

@bp.route('/login')
def new():
    token = csrf_token()
    return render_template('sessions/new.html', csrf_token=token)

@bp.route('/login', methods=['POST'])
def create():
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    email = request.form['email'].lower()
    password = request.form['password']
    users = User.find_by('email', email)
    if users and (user := users[0]) and user.authenticate(password):
        # login成功
        log_in(user)
        user_url = url_for('users.show', id=user.id, _external=True)
        return redirect(user_url)

    # login失敗
    flash('Invalid email/password combination', 'danger')
    return render_template('sessions/new.html', csrf_token=csrf_token)

# ToDo: 取り敢えずGET methodを使う。後でDELETE methodに切り替える
@bp.route('/logout', methods=['GET'])
def destroy():
    log_out()
    return redirect(url_for('static_pages.home', _external=True))
