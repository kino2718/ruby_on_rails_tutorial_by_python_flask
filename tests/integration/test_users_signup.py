from flask import render_template, url_for
import re
from sampleapp.models.user import User
from common import (is_logged_in, are_same_templates, AUTHENTICITY_TOKEN_PATTERN,
                    log_in_as)
from flask_mail import Mail

def test_invalid_signup_information(client):
    with client:
        response = client.get('/signup')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]

        before_count = User.count()
        user = User(name='', email='user@invalid',
                    password='foo', password_confirmation='bar')
        response = client.post(
            '/users', data={'name': user.name,
                            'email': user.email,
                            'password': user.password,
                            'password_confirmation': user.password_confirmation,
                            'authenticity_token': token})
        after_count = User.count()
        assert before_count == after_count

        user = User(name='', email='user@invalid',
                    password='foo', password_confirmation='bar')
        user.valid()
        ref = render_template(
            'users/new.html',user=user,csrf_token=token)
        contents = response.data.decode(encoding='utf-8')
        assert are_same_templates(ref, contents)

def test_valid_signup_information_with_account_activation(app, client):
    valid_email = 'user2@example.com'
    with client:
        try:
            response = client.get('/signup')
            contents = response.data.decode(encoding='utf-8')
            m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
            assert len(m.groups()) == 1
            token = m.groups()[0]

            before_count = User.count()
            user = User(name='Example User', email=valid_email,
                        password='password', password_confirmation='password')

            mail = Mail(app)
            with mail.record_messages() as outbox:
                response = client.post(
                    '/users', data={
                        'name': user.name,
                        'email': user.email,
                        'password': user.password,
                        'password_confirmation': user.password_confirmation,
                        'authenticity_token': token},
                    follow_redirects=True)
                assert len(outbox) == 1

            # activation状態をデータベースから読み出す
            user = User.find_by(email=user.email)[0]
            assert not user.activated

            # activation digestが作られていることを確認する
            assert user.activation_digest

            # テストからactivation tokenを使用するためにtoken, digestを再設定する
            user.activation_token = User.new_token()
            digest = User.digest(user.activation_token)
            user.update_attribute('activation_digest', digest)

            # 有効化していない状態でログインしてみる
            log_in_as(client, user.email)
            assert not is_logged_in()
            # 有効化トークンが不正な場合
            url = url_for('account_activations.edit', id='invalid token',
                          email=user.email, _external=True)
            client.get(url, follow_redirects=True)
            assert not is_logged_in()
            # トークンは正しいがメールアドレスが無効な場合
            url = url_for('account_activations.edit', id=user.activation_token,
                          email='wrong', _external=True)
            client.get(url, follow_redirects=True)
            assert not is_logged_in()
            # 有効化トークンが正しい場合
            url = url_for('account_activations.edit', id=user.activation_token,
                          email=user.email, _external=True)
            response = client.get(url, follow_redirects=True)
            contents = response.data.decode(encoding='utf-8')
            user.reload()
            assert user.activated
            ref = render_template('users/show.html',user=user)
            assert are_same_templates(ref, contents)
            assert is_logged_in()
        finally:
            # 登録したユーザーを削除
            users = User.find_by(email=valid_email)
            if users:
                users[0].destroy()
