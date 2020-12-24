from flask import g, session
from ..models.user import User

def log_in(user):
    session['id'] = user.id

def log_out():
    session.pop('id', None)
    if getattr(g, 'current_user', None):
        del g.current_user

def current_user():
    # g is unique object for each request
    current_user = getattr(g, 'current_user', None)
    user_id = session.get('id')
    if user_id:
        if not current_user:
            g.current_user = User.find(user_id)
        return g.current_user
    else:
        return None

def logged_in():
    if current_user():
        return True
    else:
        return False

def template_functions():

    return dict(current_user=current_user, logged_in=logged_in)
