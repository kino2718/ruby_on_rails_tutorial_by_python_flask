from flask import render_template, url_for
from sampleapp.models.micropost import Micropost
from common import are_same_templates, log_in_as
from flask_paginate import Pagination

def test_should_redirect_create_when_not_logged_in(client):
    with client:
        # マイクロポスト数を保存
        before_count = Micropost.count()
        response = client.post(
            '/microposts',
            data={'content': 'Lorem ipsum'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # マイクロポスト数が変わらないことを確認
        after_count = Micropost.count()
        assert before_count == after_count

        # log in画面にredirectされていることを確認
        ref = render_template('sessions/new.html')
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)

def test_should_redirect_destroy_when_not_logged_in(client, test_microposts):
    micropost = test_microposts['orange']
    with client:
        # マイクロポスト数を保存
        before_count = Micropost.count()
        response = client.post(
            f'/microposts/{micropost.id}',
            data={'_method': 'delete'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # マイクロポスト数が変わらないことを確認
        after_count = Micropost.count()
        assert before_count == after_count

        # log in画面にredirectされていることを確認
        ref = render_template('sessions/new.html')
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)

def test_should_redirect_destroy_for_wrong_micropost(client,
                                                     test_users, test_microposts):
    user = test_users['michael']
    micropost = test_microposts['ants']
    with client:
        log_in_as(client, user.email)
        before_count = Micropost.count()
        response = client.post(
            f'/microposts/{micropost.id}',
            data={'_method': 'delete'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # マイクロポスト数が変わらないことを確認
        after_count = Micropost.count()
        assert before_count == after_count
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
