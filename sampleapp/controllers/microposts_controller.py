from flask import (Blueprint, abort, request, flash, redirect, url_for,
                   render_template, current_app)
from ..controllers.users_controller import logged_in_user
from ..helpers.application_helper import check_csrf_token
from ..helpers.sessions_helper import current_user
from flask_paginate import Pagination, get_page_parameter

bp = Blueprint('microposts', __name__, url_prefix='/microposts')

@bp.route('', methods=['POST'])
@logged_in_user
def create():
    csrf_token = check_csrf_token()
    if not csrf_token:
        abort(422)

    content = request.form['content']
    micropost = current_user().microposts.build(content=content)
    image_file = request.files.get('image')
    #print(f'\n**** image ****\n{image_file}, {not(not(image_file))}\n')
    micropost.image_attach(image_file)
    if micropost.save():
        flash('Micropost created!', 'success')
        root_url = url_for('static_pages.home', _external=True)
        return redirect(root_url)
    else:
        feed_items = current_user().feed()
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 30
        total = len(feed_items)
        feed_items = feed_items[(page-1)*per_page:page*per_page]
        pagination = Pagination(
            page=page, total=total, per_page=per_page,
            href=url_for('static_pages.home')+'?page={0}',
            prev_label='&larr; Previous', next_label='Next &rarr;',
            css_framework='bootstrap3')
        return render_template('static_pages/home.html',
                               micropost=micropost, feed_items=feed_items,
                               pagination=pagination, csrf_token=csrf_token)

@bp.route('/<int:id>', methods=['POST'])
@logged_in_user
def destroy(id):
    method = request.form.get('_method').lower()
    if method != 'delete':
        url = url_for('static_pages.home', _external=True)
        return redirect(url)

    microposts = current_user().microposts.find_by(id=id)
    if not microposts:
        url = url_for('static_pages.home', _external=True)
        return redirect(url)

    micropost = microposts[0]
    micropost.destroy()
    flash('Micropost deleted', 'success')
    url = request.referrer or url_for('static_pages.home', _external=True)
    return redirect(url)
