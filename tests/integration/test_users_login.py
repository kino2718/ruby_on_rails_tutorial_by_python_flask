import pytest
from flask import render_template, get_flashed_messages
import re
from sampleapp.models.user import User
from sampleapp.helpers.sessions_helper import logged_in

AUTHENTICITY_TOKEN_PATTERN = re.compile(r'name="authenticity_token" value="(.*)"')

# テスト用のユーザーをデータベースに追加。テストが終了したら削除。
@pytest.fixture
def test_user():
    test_user = None
    try:
        user = User(name='foobar',
                    email='foo@bar.com',
                    password='password',
                    password_confirmation='password')
        print(f'**** user: {user} ****')
        if user.save():
            print(f'**** user saved ****')
            users = User.find_by('email', 'foo@bar.com')
            print(f'**** users: {users} ****')
            test_user = users[0]
            print(f'**** test user: {test_user} ****')
        yield test_user
    finally:
        if test_user:
            print(f'**** destroy user ****')
            test_user.destroy()

def  test_login_with_valid_email_invalid_password(client, test_user):
    with client:
        # ログインページの表示
        response = client.get('/login')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        # ログインページが表示されたことを確認
        ref = render_template('sessions/new.html', csrf_token=token)
        assert response.data == ref.encode(encoding='utf-8')

        # 無効なデータでログインを行う
        response = client.post(
            '/login', data={'email': test_user.email,
                            'password': '',
                            'authenticity_token': token})
        # ログインしてないことを確認
        assert not logged_in()
        # ログインページに戻されることを確認
        ref = render_template('sessions/new.html', csrf_token=token)
        assert response.data == ref.encode(encoding='utf-8')

        # flashメッセージが存在することを確認
        flashed_message = get_flashed_messages()
        assert flashed_message

        # Homeに移動しflashメッセージが消えていることを確認
        response = client.get('/')
        flashed_message = get_flashed_messages()
        assert not flashed_message

def test_login_with_valid_information(client, test_user):
    with client:
        # ログインページの表示
        response = client.get('/login')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]

        # 登録ユーザーでログインを行う
        response = client.post(
            '/login', data={'email': test_user.email,
                            'password': 'password',
                            'authenticity_token': token},
            follow_redirects=True)

        # ログインしていることを確認
        assert logged_in()

        # redirectされていることを確認
        ref = render_template('users/show.html', user=test_user)
        assert response.data == ref.encode(encoding='utf-8')

        # login へのリンクが無いことを確認
        m = re.search(r'<a.*href="/login"', response.data.decode('utf-8'))
        assert not m

        # logout へのリンクがあることを確認
        m = re.search(r'<a.*href="/logout"', response.data.decode('utf-8'))
        assert m

        # プロフィールへのリンクがあることを確認
        m = re.search(rf'<a.*(href="/users/{test_user.id}")', response.data.decode('utf-8'))
        assert m

        # ログアウトを実行
        response = client.get('/logout', follow_redirects=True)

        # ログアウトしたことを確認
        assert not logged_in()

        # Homeページへリダイレクトしたことを確認
        ref = render_template('static_pages/home.html')
        assert response.data == ref.encode(encoding='utf-8')

        # login へのリンクがあることを確認
        m = re.search(r'<a.*href="/login"', response.data.decode('utf-8'))
        assert m

        # logout へのリンクが無いことを確認
        m = re.search(r'<a.*href="/logout"', response.data.decode('utf-8'))
        assert not m

        # プロフィールへのリンクが無いことを確認
        m = re.search(rf'<a.*(href="/users/{test_user.id}")', response.data.decode('utf-8'))
        assert not m
