from flask import (Blueprint, render_template, session, request, abort,
                   redirect, url_for, flash)
from ..models.user import User
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
    token = secrets.token_hex()
    session[_CSRF_TOKEN] = token
    return render_template('users/new.html', user=User(), csrf_token=token)

@bp.route('', methods=['POST'])
def create():
    csrf_token = request.form.get('authenticity_token')
    right_csrf_token = session[_CSRF_TOKEN]
    if (csrf_token != right_csrf_token):
        abort(422)

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']
    user = User(name=name, email=email, password=password,
                password_confirmation=password_confirmation)

    if user.save():
        user_url = url_for('.show',id=user.id, _external=True)
        flash('Welcome to the Sample App!', 'success')
        return redirect(user_url)
    else:
        return render_template('users/new.html', user=user, csrf_token=csrf_token)
