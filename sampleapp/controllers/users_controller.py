from flask import Blueprint, render_template

bp = Blueprint('users', __name__, url_prefix='/')

@bp.route('/signup')
def new():
    return render_template('users/new.html')
