from flask import render_template, get_flashed_messages
from common import AUTHENTICITY_TOKEN_PATTERN, are_same_templates, is_logged_in
import re
from flask_mail import Mail
from sampleapp.models.user import User

def test_password_resets(app, client, test_users):
    user = test_users['michael']
    with client:
        response = client.get('/password_resets/new')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        ref = render_template(
            'password_resets/new.html')
        assert are_same_templates(ref, contents)
        assert re.search(r'<input .*name="email" ', contents)

        # メールアドレスが無効
        response = client.post(
            '/password_resets', data={'email': "",
                                      'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]

        # flashメッセージが存在することを確認
        flashed_message = get_flashed_messages()
        assert flashed_message
        ref = render_template(
            'password_resets/new.html')

        # メールアドレスが有効
        mail = Mail(app)
        with mail.record_messages() as outbox:
            response = client.post(
                '/password_resets', data={'email': user.email,
                                          'authenticity_token': token},
                follow_redirects=True)
            contents = response.data.decode(encoding='utf-8')
            assert user.reset_digest != user.reload().reset_digest
            assert len(outbox) == 1

        flashed_message = get_flashed_messages()
        assert flashed_message
        ref = render_template(
            'static_pages/home.html')
        assert are_same_templates(ref, contents)

        # パスワード再設定フォームのテスト
        # テスト用にreset token, digestを再設定する
        user.reset_token = User.new_token()
        digest = User.digest(user.reset_token)
        user.update_attribute('reset_digest', digest)

        # メールアドレスが無効
        response = client.get(
            f'/password_resets/{user.reset_token}/edit?email=',
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        ref = render_template(
            'static_pages/home.html')
        assert are_same_templates(ref, contents)

        # 無効なユーザー
        user.update_attribute('activated', False)
        response = client.get(
            f'/password_resets/{user.reset_token}/edit?email={user.email}',
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        ref = render_template(
            'static_pages/home.html')
        assert are_same_templates(ref, contents)
        user.update_attribute('activated', True)

        # メールアドレスが有効で、トークンが無効
        response = client.get(
            f'/password_resets/wrong_token/edit?email={user.email}',
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        ref = render_template(
            'static_pages/home.html')
        assert are_same_templates(ref, contents)

        # メールアドレスもトークンも有効
        response = client.get(
            f'/password_resets/{user.reset_token}/edit?email={user.email}',
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        ref = render_template(
            'password_resets/edit.html',
            user=user, reset_token=user.reset_token)
        assert are_same_templates(ref, contents)
        assert re.search(rf'<input type="hidden" name="email" value="{user.email}"',
                         contents)

        # 無効なパスワードとパスワード確認
        response = client.post(
            f'/password_resets/{user.reset_token}',
            data={'_method': 'patch',
                  'email': user.email,
                  'password': 'foobaz',
                  'password_confirmation': 'barquux',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        assert re.search(r'<div id="error_explanation"', contents)

        # パスワードが空
        response = client.post(
            f'/password_resets/{user.reset_token}',
            data={'_method': 'patch',
                  'email': user.email,
                  'password': '',
                  'password_confirmation': '',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        assert re.search(r'<div id="error_explanation"', contents)

        # 有効なパスワードとパスワード確認
        response = client.post(
            f'/password_resets/{user.reset_token}',
            data={'_method': 'patch',
                  'email': user.email,
                  'password': 'foobaz',
                  'password_confirmation': 'foobaz',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        assert is_logged_in()
        flashed_message = get_flashed_messages()
        assert flashed_message
        ref = render_template('users/show.html',user=user)
        assert are_same_templates(ref, contents)
