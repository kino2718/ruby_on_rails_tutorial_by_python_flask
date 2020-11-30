from flask import Blueprint, render_template

bp = Blueprint('static_pages', __name__, url_prefix='/static_pages')

@bp.route('/home')
def home():
    return render_template('static_pages/home.html')

@bp.route('help')
def help():
    return render_template('static_pages/help.html')
