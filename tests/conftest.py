import pytest
from sampleapp import create_app
from sampleapp.models.user import User
import yaml

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

# テスト用のユーザーuser.ymlから読み込みデータベースに追加。テストが終了したら削除。
@pytest.fixture
def test_users():
    test_users = {}
    try:
        with open('tests/fixtures/users.yml') as f:
            data = yaml.safe_load(f)

        for k,v in data.items():
            name=v['name']
            email=v['email']
            password = v['password']
            user = User(name=name, email=email, password=password,
                        password_confirmation=password)
            if user.save():
                user.reload()
                test_users[k] = user
        #print(f'\n**** test users: {test_users} ****\n')
        yield test_users
    finally:
        for user in test_users.values():
            user.destroy()
