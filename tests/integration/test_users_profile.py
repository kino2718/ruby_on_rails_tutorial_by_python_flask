from flask import url_for, render_template
from flask_paginate import Pagination
from common import are_same_templates
import re

def test_profile_display(app, client, test_users, test_microposts):
    user = test_users['michael']
    with client:
        client.get('/') # url_forを使うのに一度どこかのページにアクセスする
        url = url_for('users.show', id=user.id)
        response = client.get(url)
        contents = response.data.decode(encoding='utf-8')
        page = 1
        per_page = 30
        microposts = user.microposts()
        total = len(microposts)
        microposts = microposts[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, total=total, per_page=per_page,
                                prev_label='&larr; Previous',
                                next_label='Next &rarr;',
                                css_framework='bootstrap3')
        ref = render_template('users/show.html',
                              user=user,
                              microposts=microposts,
                              pagination=pagination)
        assert are_same_templates(ref, contents)
        assert re.search(rf'<title>{user.name}', contents)
        assert re.search(rf'<h1>.*{user.name}.*</h1>', contents, flags=re.DOTALL)
        assert re.search(rf'<h1>.*<img .*gravatar.*>.*</h1>', contents,
                         flags=re.DOTALL)
        assert re.search(rf'Microposts \({user.microposts.count()}\)', contents)
        assert re.search(rf'class="pagination"', contents)
        for m in microposts:
            assert re.search(m.content, contents)
