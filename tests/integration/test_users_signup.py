from flask import render_template
import re
from sampleapp.models.user import User
from sampleapp.helpers.sessions_helper import logged_in

AUTHENTICITY_TOKEN_PATTERN = re.compile(r'name="authenticity_token" value="(.*)"')

def test_invalid_signup_information(client, are_same_templates):
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

def test_valid_signup_information(client, are_same_templates):
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
            response = client.post(
                '/users', data={'name': user.name,
                                'email': user.email,
                                'password': user.password,
                                'password_confirmation': user.password_confirmation,
                                'authenticity_token': token},
                follow_redirects=True)
            after_count = User.count()
            assert before_count+1 == after_count

            user.valid()
            ref = render_template('users/show.html',user=user)
            contents = response.data.decode(encoding='utf-8')
            assert are_same_templates(ref, contents)
            assert logged_in()
        finally:
            # 登録したユーザーを削除
            users = User.find_by('email', valid_email)
            if users:
                users[0].destroy()
