from flask import (Blueprint, render_template, session, request, abort,
                   redirect, url_for, flash)
from ..models.user import User
from ..helpers.application_helper import csrf_token, check_csrf_token
from ..helpers.sessions_helper import log_in
import secrets

bp = Blueprint('users', __name__, url_prefix='/users')

_CSRF_TOKEN= 'csrf_token'

@bp.route('/<int:id>')
def show(id):
    user = User.find(id)
    if user is None:
        abort(404)
    return render_template('users/show.html', user=user)

@bp.route('/new')
def new():
    token = csrf_token()
    return render_template('users/new.html', user=User(), csrf_token=token)

@bp.route('', methods=['POST'])
def create():
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']
    user = User(name=name, email=email, password=password,
                password_confirmation=password_confirmation)

    if user.save():
        log_in(user)
        user_url = url_for('.show',id=user.id, _external=True)
        flash('Welcome to the Sample App!', 'success')
        return redirect(user_url)
    else:
        return render_template('users/new.html', user=user, csrf_token=csrf_token)

@bp.route('/<int:id>/edit')
def edit(id):
    user = User.find(id)
    if user is None:
        abort(404)
    token = csrf_token()
    return render_template('users/edit.html', user=user, csrf_token=token)

@bp.route('/<int:id>', methods=['POST'])
def handle_method(id):
    # formの_method要素の値でメソッドを判断する
    method = request.form.get('_method').lower()
    if method == 'patch':
        return update(id)

    # 対応していないメソッドだったらユーザーの情報を表示するページにリダイレクト
    user_url = url_for('.show',id=id, _external=True)
    return redirect(user_url)

def update(id):
    # CSRF対策
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    user = User.find(id)
    if user is None:
        abort(404)

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    if user.update(name=name, email=email, password=password,
                password_confirmation=password_confirmation):
        user_url = url_for('.show',id=user.id, _external=True)
        flash('Profile updated', 'success')
        return redirect(user_url)
    else:
        return render_template('users/edit.html', user=user, csrf_token=csrf_token)
