from flask import render_template, request
from common import are_same_templates, log_in_as
from flask_paginate import Pagination
from sampleapp.models.user import User
import re

def test_index_including_pagination(client, test_users):
    user = test_users['michael']
    with client:
        # ログインする
        log_in_as(client, user.email)

        # ユーザー一覧ページにアクセス
        response = client.get('/users', follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')

        # ユーザー一覧ページが表示されたことを確認
        page = 1
        per_page = 30
        users = User.all()
        total = len(users)
        users = users[(page-1)*per_page:page*per_page]
        # Pagination内でview_argsにアクセスしているがtest_clientコンテキストでは
        # 存在しないのでエラーにならないようダミーを設定する
        request.view_args = {}
        pagination = Pagination(page=page, total=total, per_page=per_page,
                                prev_label='&larr; Previous',
                                next_label='Next &rarr;',
                                css_framework='bootstrap3')
        ref = render_template('users/index.html', users=users, pagination=pagination)
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)

        assert re.search(r'class="pagination"', contents)

        for user in User.paginate(page=page):
            assert re.search(f'<a href="/users/{user.id}">{user.name}', contents)
