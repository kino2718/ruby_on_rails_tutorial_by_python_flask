import pytest
from sampleapp.models.user import User
from sampleapp.helpers.sessions_helper import current_user, remember
from flask import current_app, request
from itsdangerous import URLSafeSerializer
from common import is_logged_in

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

def remember(user):
    # 強引にcookieを変更する
    request.cookies = dict()
    user.remember()
    key = current_app.secret_key
    s = URLSafeSerializer(key, salt='remember_me')
    signed_id = s.dumps(user.id)
    request.cookies['user_id'] = signed_id
    request.cookies['remember_token'] = user.remember_token

def test_current_user_returns_right_user_when_session_is_nil(app, test_user):
    with app.test_request_context('/'):
        remember(test_user)
        cur = current_user()
        assert cur
        assert test_user == cur
        assert is_logged_in()

def test_current_user_returns_nil_when_remember_digest_is_wrong(app, test_user):
    with app.test_request_context('/'):
        remember(test_user)
        test_user.update_attribute(remember_digest=User.digest(User.new_token()))
        assert not current_user()
