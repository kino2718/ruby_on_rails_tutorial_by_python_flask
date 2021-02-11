from flask import (Blueprint, render_template, session, request, abort,
                   redirect, url_for, flash, current_app)
from ..models.user import User
from ..helpers.application_helper import csrf_token, check_csrf_token
from ..helpers.sessions_helper import (logged_in, is_current_user,
                                       store_location, current_user)
import secrets
import functools
from flask_paginate import Pagination, get_page_parameter

bp = Blueprint('users', __name__, url_prefix='/users')

# decorator
def logged_in_user(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not logged_in():
            store_location()
            flash('Please log in', 'danger')
            login_url = url_for('sessions.new', _external=True)
            return redirect(login_url)
        return f(*args, **kwargs)
    return wrapper

# decorator
def correct_user(f):
    @functools.wraps(f)
    def wrapper(id, *args, **kwargs):
        user = User.find(id)
        if not is_current_user(user):
            url = url_for('static_pages.home', _external=True)
            return redirect(url)
        return f(id, *args, **kwargs)
    return wrapper

# decorator
def admin_user(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user and user.admin:
            return f(*args, **kwargs)
        user_url = url_for('static_pages.home', _external=True)
        return redirect(user_url)
    return wrapper

@bp.route('/')
@logged_in_user
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 30
    # 全ユーザー数を取得するUser.countメソッドでどのみちUser.allを呼び出すので
    # paginateは使用しないでUser.allを使用する
    #users = User.paginate(page)
    users = User.all()
    total = len(users)
    users = users[(page-1)*per_page:page*per_page]
    # User.paginateを使う場合
    # pagination = Pagination(page=page, total=User.count(), per_page=per_page,
    #                         prev_label='&larr; Previous', next_label='Next &rarr;',
    #                         css_framework='bootstrap3')
    pagination = Pagination(page=page, total=total, per_page=per_page,
                            prev_label='&larr; Previous', next_label='Next &rarr;',
                            css_framework='bootstrap3')
    return render_template('users/index.html', users=users, pagination=pagination)

@bp.route('/<int:id>')
def show(id):
    user = User.find(id)
    if user is None:
        abort(404)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 30
    microposts = user.microposts()
    total = len(microposts)
    microposts = microposts[(page-1)*per_page:page*per_page]
    pagination = Pagination(page=page, total=total, per_page=per_page,
                            prev_label='&larr; Previous', next_label='Next &rarr;',
                            css_framework='bootstrap3')
    token = csrf_token()
    return render_template('users/show.html', user=user, microposts=microposts,
                           pagination=pagination, csrf_token=token)

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
        try:
            user.send_activation_email(current_app)
        except ConnectionRefusedError as e:
            user.destroy()
            abort(500, description='Unable to send the confirmation email')
        except BaseException as e:
            user.destroy()
            raise e

        flash('Please check your email to activate your account.', 'info')
        root_url = url_for('static_pages.home', _external=True)
        return redirect(root_url)
    else:
        return render_template('users/new.html', user=user, csrf_token=csrf_token)

@bp.route('/<int:id>/edit')
@logged_in_user
@correct_user
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
    elif method == 'delete':
        return destroy(id)

    # 対応していないメソッドだったらユーザーの情報を表示するページにリダイレクト
    user_url = url_for('.show',id=id, _external=True)
    return redirect(user_url)

@logged_in_user
@correct_user
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

@logged_in_user
@admin_user
def destroy(id):
    user = User.find(id)
    if user is None:
        abort(404)

    user.destroy()
    flash('User deleted', 'success')
    users_url = url_for('.index', _external=True)
    return redirect(users_url)

@bp.route('/<int:id>/following')
@logged_in_user
def following(id):
    title = 'Following'
    user = User.find(id)
    users = user.following()
    return render_template('users/show_follow.html', title=title, user=user,
                           users=users)

@bp.route('/<int:id>/followers')
@logged_in_user
def followers(id):
    title = 'Followers'
    user = User.find(id)
    users = user.followers()
    return render_template('users/show_follow.html', title=title, user=user,
                           users=users)
