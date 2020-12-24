import pytest
from flask import render_template
import re
from sampleapp.models.user import User
import time

AUTHENTICITY_TOKEN_PATTERN = re.compile(r'name="authenticity_token" value="(.*)"')
WAIT_UNTIL_DATA_PROCESSED = 5

# 危険なので削除。必要なら手動で行う。
# @pytest.fixture
# def delete_all_users_after_test(autouse=True):
#     yield
#     users = User.all()
#     for user in users:
#         user.destroy()
#         time.sleep(WAIT_UNTIL_DATA_PROCESSED)

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
        time.sleep(WAIT_UNTIL_DATA_PROCESSED)
        after_count = User.count()
        assert before_count == after_count

        user = User(name='', email='user@invalid',
                    password='foo', password_confirmation='bar')
        user.valid()
        ref = render_template(
            'users/new.html',user=user,csrf_token=token).encode(encoding='utf-8')
        #print(f'**** response ****\n{response.data}')
        #print(f'**** ref ****\n{ref}')
        assert response.data == ref

def test_valid_signup_information(client):
    with client:
        response = client.get('/signup')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]

        before_count = User.count()
        user = User(name='Example User', email='user@example.com',
                    password='password', password_confirmation='password')
        response = client.post(
            '/users', data={'name': user.name,
                            'email': user.email,
                            'password': user.password,
                            'password_confirmation': user.password_confirmation,
                            'authenticity_token': token},
            follow_redirects=True)
        time.sleep(WAIT_UNTIL_DATA_PROCESSED)
        after_count = User.count()
        assert before_count+1 == after_count

        user.valid()
        ref = render_template(
            'users/show.html',user=user).encode(encoding='utf-8')
        assert response.data == ref

        # 登録したユーザーを削除
        users = User.find_by('email', 'user@example.com')
        if users:
            users[0].destroy()
