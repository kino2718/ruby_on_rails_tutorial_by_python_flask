import pytest
from sampleapp import create_app
from sampleapp.models.user import User

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

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
