from flask import (Blueprint, render_template, request, flash, redirect,
                   current_app, url_for, abort)
from ..helpers.application_helper import csrf_token, check_csrf_token
from ..helpers.sessions_helper import log_in
from ..models.user import User

bp = Blueprint('password_resets', __name__, url_prefix='/password_resets')

@bp.route('/new')
def new():
    token = csrf_token()
    return render_template('password_resets/new.html', csrf_token=token)

@bp.route('', methods=['POST'])
def create():
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    email = request.form['email']
    users = User.find_by(email=email)
    if users and (user:=users[0]):
        user.create_reset_digest()
        user.send_password_reset_email(current_app)
        flash('Email sent with password reset instructions', 'info')
        url = url_for('static_pages.home', _external=True)
        return redirect(url)
    else:
        flash('Email address not found', 'danger')
        return render_template('password_resets/new.html', csrf_token=csrf_token)

@bp.route('/<id>/edit')
def edit(id):
    email = request.args.get('email')
    users = User.find_by(email=email)
    if not (users and (user:=users[0]) and user.activated and \
            user.authenticated('reset', id)):
        url = url_for('static_pages.home', _external=True)
        return redirect(url)

    if user.password_reset_expired():
        flash('Password reset has expired.', 'danger')
        url = url_for('.new', _external=True)
        return redirect(url)

    token = csrf_token()
    return render_template('password_resets/edit.html',
                           user=user, reset_token=id, csrf_token=token)


@bp.route('/<id>', methods=['POST'])
def update(id):
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    method = request.form['_method'].lower()
    if method != 'patch':
        url = url_for('static_pages.home', _external=True)
        return redirect(url)

    email = request.form.get('email')
    users = User.find_by(email=email)
    if not (users and (user:=users[0]) and user.activated and \
            user.authenticated('reset', id)):
        url = url_for('static_pages.home', _external=True)
        return redirect(url)

    if user.password_reset_expired():
        flash('Password reset has expired.', 'danger')
        url = url_for('.new', _external=True)
        return redirect(url)

    password = request.form['password']
    password_confirmation = request.form['password_confirmation']
    if not password:
        user.errors.add('password', "password can't be blank")
        return render_template('password_resets/edit.html',
                               user=user, reset_token=id, csrf_token=csrf_token)
    elif user.update(password=password, password_confirmation=password_confirmation):
        log_in(user)
        flash('Password has been reset.', 'success')
        url = url_for('users.show', id=user.id, _external=True)
        return redirect(url)
    else:
        return render_template('password_resets/edit.html',
                               user=user, reset_token=id, csrf_token=csrf_token)
