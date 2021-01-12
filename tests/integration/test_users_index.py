from flask import render_template, request
from common import are_same_templates, log_in_as
from flask_paginate import Pagination
from sampleapp.models.user import User
import re

def test_index_as_admin_including_pagination_and_delete_links(client, test_users):
    admin = test_users['michael']
    non_admin = test_users['archer']
    with client:
        # adminとしてログインする
        log_in_as(client, admin.email)

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

        # paginationクラスの要素があることを確認
        assert re.search(r'class="pagination"', contents)

        # 最初のページに含まれるユーザーが表示されていることを確認
        for user in User.paginate(page=page):
            assert re.search(f'<a href="/users/{user.id}">{user.name}', contents)

        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token

        # ユーザー数を保存する
        before_count = User.count()

        # delete method を投げる
        response = client.post(
            f'/users/{non_admin.id}',
            data={'_method': 'delete',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')

        # ユーザーが一人減ったことを確認する
        after_count = User.count()
        assert before_count-1 == after_count

def test_index_as_non_admin(client, test_users):
    non_admin = test_users['archer']
    with client:
        # 一般ユーザーとしてログインする
        log_in_as(client, non_admin.email)

        # ユーザー一覧ページにアクセス
        response = client.get('/users', follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')

        # deleteリンクが表示されていないことを確認
        assert not re.search(r'<a .*>delete</a>', contents)
