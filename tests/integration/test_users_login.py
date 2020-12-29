import pytest
from flask import render_template, get_flashed_messages, request
import re
from sampleapp.models.user import User
from common import is_logged_in, are_same_templates, log_in_as, log_out

# テスト用のユーザーをデータベースに追加。テストが終了したら削除。
@pytest.fixture
def test_user():
    test_user = None
    try:
        user = User(name='foobar',
                    email='foo@bar.com',
                    password='password',
                    password_confirmation='password')
        if user.save():
            users = User.find_by('email', 'foo@bar.com')
            test_user = users[0]
        yield test_user
    finally:
        if test_user:
            test_user.destroy()

def  test_login_with_valid_email_invalid_password(client, test_user):
    with client:
        # 無効なデータでログインを行う
        response = log_in_as(client, test_user.email, password='')

        # ログインしてないことを確認
        assert not is_logged_in()

        # ログインページに戻されることを確認
        ref = render_template('sessions/new.html')
        assert are_same_templates(
            ref,
            response.data.decode(encoding='utf-8'))

        # flashメッセージが存在することを確認
        flashed_message = get_flashed_messages()
        assert flashed_message

        # Homeに移動しflashメッセージが消えていることを確認
        response = client.get('/')
        flashed_message = get_flashed_messages()
        assert not flashed_message

def test_login_with_valid_information_followed_by_logout(client, test_user):
    with client:
        # 登録ユーザーでログインを行う
        response = log_in_as(client, test_user.email, 'password')

        # ログインしていることを確認
        assert is_logged_in()

        # redirectされていることを確認
        ref = render_template('users/show.html', user=test_user)
        contents = response.data.decode(encoding='utf-8')
        assert are_same_templates(ref, contents)

        # login へのリンクが無いことを確認
        m = re.search(r'<a.*href="/login"', response.data.decode('utf-8'))
        assert not m

        # logout へのリンクがあることを確認
        m = re.search(r'<a.*href="/logout"', response.data.decode('utf-8'))
        assert m

        # プロフィールへのリンクがあることを確認
        m = re.search(rf'<a.*(href="/users/{test_user.id}")', response.data.decode('utf-8'))
        assert m

        # ログアウト
        response = log_out(client, contents)

        # ログアウトしたことを確認
        assert not is_logged_in()

        # Homeページへリダイレクトしたことを確認
        ref = render_template('static_pages/home.html')
        assert are_same_templates(
            ref,
            response.data.decode(encoding='utf-8'))

        # 2番目のウィンドウでログアウトをクリックするユーザーをシミュレートする
        contents = response.data.decode(encoding='utf-8')
        response = log_out(client, contents)

        # login へのリンクがあることを確認
        m = re.search(r'<a.*href="/login"', response.data.decode('utf-8'))
        assert m

        # logout へのリンクが無いことを確認
        m = re.search(r'<a.*href="/logout"', response.data.decode('utf-8'))
        assert not m

        # プロフィールへのリンクが無いことを確認
        m = re.search(rf'<a.*(href="/users/{test_user.id}")', response.data.decode('utf-8'))
        assert not m

def test_login_with_remembering(client, test_user):
    with client:
        log_in_as(client, test_user.email, remember_me='1')
        assert request.cookies.get('remember_token')

def test_login_without_remembering(client, test_user):
    with client:
        # cookieを保存してログイン
        response = log_in_as(client, test_user.email, remember_me='1')
        contents = response.data.decode(encoding='utf-8')

        # ログアウト
        response = log_out(client, contents)

        # cookieを削除してログイン
        log_in_as(client, test_user.email, remember_me='0')
        assert not request.cookies.get('remember_token')
