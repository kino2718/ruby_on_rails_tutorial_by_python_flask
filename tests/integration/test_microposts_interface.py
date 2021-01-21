from common import log_in_as, are_same_templates
import re
from sampleapp.models.micropost import Micropost
from flask import render_template, url_for
from flask_paginate import Pagination

def test_micropost_interface(client, test_users, test_microposts):
    user = test_users['michael']
    with client:
        log_in_as(client, user.email)
        response = client.get('/')
        contents = response.data.decode(encoding='utf-8')
        assert re.search('pagination', contents)
        # 無効な送信
        before_count = Micropost.count()
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        response = client.post(
            '/microposts',
            data={'content': '',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # マイクロポスト数が変わらないことを確認
        after_count = Micropost.count()
        assert before_count == after_count
        #print(f'\n{contents}\n')
        assert re.search('error_explanation', contents)
        assert re.search(r'<a href="/\?page=2">', contents)
        # 有効な送信
        before_count = Micropost.count()
        content = "This micropost really ties the room together"
        response = client.post(
            '/microposts',
            data={'content': content,
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # マイクロポスト数が1増えたことを確認
        after_count = Micropost.count()
        assert before_count+1 == after_count
        # home画面にredirectされていることを確認
        micropost = user.microposts.build()
        feed_items = user.feed()
        page = 1
        per_page = 30
        total = len(feed_items)
        feed_items = feed_items[(page-1)*per_page:page*per_page]
        pagination = Pagination(
            page=page, total=total, per_page=per_page,
            href=url_for('static_pages.home')+'?page={0}',
            prev_label='&larr; Previous', next_label='Next &rarr;',
            css_framework='bootstrap3')
        ref = render_template('static_pages/home.html',
                              micropost=micropost, feed_items=feed_items,
                              pagination=pagination)
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)
        assert re.search(content, contents)
        # 投稿を削除する
        before_count = Micropost.count()
        assert re.search(r'<a.*>delete</a>', contents)
        first_micropost = user.microposts()[0]
        response = client.post(
            f'/microposts/{first_micropost.id}',
            data={'_method': 'delete'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = Micropost.count()
        assert before_count-1 == after_count
        user2 = test_users['archer']
        response = client.get(f'/users/{user2.id}',
                              follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        print(f'\n{contents}\n')
        assert not re.search(r'<a.*>delete</a>', contents)
