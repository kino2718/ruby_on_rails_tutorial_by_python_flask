from flask import Blueprint, render_template

# 1st arg: The name of the blueprint. Will be prepended to each endpoint name.
bp = Blueprint('static_pages', __name__, url_prefix='/')

@bp.route('/')
def home():
    return render_template('static_pages/home.html')

@bp.route('/help')
def help():
    return render_template('static_pages/help.html')

@bp.route('/about')
def about():
    return render_template('static_pages/about.html')

@bp.route('/contact')
def contact():
    return render_template('static_pages/contact.html')
