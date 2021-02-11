from flask import Blueprint, request, abort, url_for, redirect
from .users_controller import logged_in_user
from ..helpers.application_helper import check_csrf_token, csrf_token
from ..helpers.sessions_helper import current_user
from ..models.user import User
from ..models.relationship import Relationship

bp = Blueprint('relationships', __name__, url_prefix='/relationships')

@bp.route('', methods=['POST'])
@logged_in_user
def create():
    # CSRF対策
    token = check_csrf_token()
    if not token:
        abort(422)

    id = request.form['followed_id']
    id = int(id)
    user = User.find(id)
    if user is None:
        abort(404)

    cur = current_user()
    cur.follow(user)

    accept = request.headers.get('Accept', '')
    if accept and accept.lower() == 'application/json':
        return {'result':'ok',
                'followers': len(user.followers()),
                'relation_id': cur.active_relationships_find_by(user.id).id,
                'csrf_token': csrf_token()
                }
    else:
        url = url_for('users.show', id=user.id, _external=True)
        return redirect(url)

@bp.route('/<int:id>', methods=['POST'])
@logged_in_user
def destroy(id):
    # CSRF対策
    token = check_csrf_token()
    if not token:
        abort(422)

    user = Relationship.find(id).followed()
    if user is None:
        abort(404)

    current_user().unfollow(user)

    accept = request.headers.get('Accept', '')
    if accept and accept.lower() == 'application/json':
        return {'result':'ok',
                'followers': len(user.followers()),
                'user_id': user.id,
                'csrf_token': csrf_token()
        }
    else:
        url = url_for('users.show', id=user.id, _external=True)
        return redirect(url)
