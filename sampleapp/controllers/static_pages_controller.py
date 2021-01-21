from flask import Blueprint, render_template, request
from ..helpers.sessions_helper import logged_in, current_user
from ..helpers.application_helper import csrf_token
from flask_paginate import Pagination, get_page_parameter

# 1st arg: The name of the blueprint. Will be prepended to each endpoint name.
bp = Blueprint('static_pages', __name__, url_prefix='/')

@bp.route('/')
def home():
    micropost = feed_items = pagination = token = None
    if logged_in():
        token = csrf_token()
        user = current_user()
        micropost = user.microposts.build()
        feed_items = user.feed()
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 30
        total = len(feed_items)
        feed_items = feed_items[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, total=total, per_page=per_page,
                            prev_label='&larr; Previous', next_label='Next &rarr;',
                            css_framework='bootstrap3')
    return render_template('static_pages/home.html',
                           micropost=micropost, feed_items=feed_items,
                           pagination=pagination, csrf_token=token)

@bp.route('/help')
def help():
    return render_template('static_pages/help.html')

@bp.route('/about')
def about():
    return render_template('static_pages/about.html')

@bp.route('/contact')
def contact():
    return render_template('static_pages/contact.html')
