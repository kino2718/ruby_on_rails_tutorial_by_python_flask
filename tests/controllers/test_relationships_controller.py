from flask import render_template
from sampleapp.models.relationship import Relationship
from common import are_same_templates

def test_create_should_require_logged_in_user(client, test_users,
                                              test_relationships):
    user = test_users['michael']
    with client:
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        before_count = Relationship.count()
        response = client.post(
            '/relationships',
            data={'followed_id': user.id,
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = Relationship.count()
        assert before_count == after_count
        # log in画面にredirectされていることを確認
        ref = render_template('sessions/new.html', csrf_token=token)
        assert are_same_templates(ref, contents)

def test_destroy_should_require_logged_in_user(client, test_users,
                                               test_relationships):
    relationship = test_relationships['one']
    with client:
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        before_count = Relationship.count()
        response = client.post(
            f'/relationships/{relationship.id}',
            data={'_method': 'delete',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = Relationship.count()
        assert before_count == after_count
        # log in画面にredirectされていることを確認
        ref = render_template('sessions/new.html', csrf_token=token)
        assert are_same_templates(ref, contents)
