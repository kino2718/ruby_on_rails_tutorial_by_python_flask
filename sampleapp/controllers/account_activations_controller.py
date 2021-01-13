from flask import Blueprint, request, flash, url_for, redirect
from ..models.user import User
from datetime import datetime
from ..helpers.sessions_helper import log_in

bp = Blueprint('account_activations', __name__, url_prefix='/')

@bp.route('/<id>/edit')
def edit(id):
    email = request.args.get('email')
    users = User.find_by('email', email)
    if users and (user:=users[0]) and not user.activated and \
       user.authenticated('activation', id):
        user.activate()
        log_in(user)
        flash('Account activated!', 'success')
        url = url_for('users.show', id=user.id, _external=True)
        return redirect(url)
    else:
        flash('Invalid activation link', 'danger')
        url = url_for('static_pages.home', _external=True)
        return redirect(url)
