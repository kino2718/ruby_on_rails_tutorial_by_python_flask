import pytest
from sampleapp import create_app
from sampleapp.models.user import User
from sampleapp.models.micropost import Micropost
import yaml
from datetime import datetime, timezone
from faker import Faker

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
            admin = v.get('admin', False)
            activated = v.get('activated', False)
            activated_at = None
            if activated:
                activated_at = datetime.now(timezone.utc)
            user = User(name=name, email=email, password=password,
                        password_confirmation=password, admin=admin,
                        activated=activated, activated_at=activated_at)
            if user.save():
                user.reload()
                test_users[k] = user
        #print(f'\n**** test users: {test_users} ****\n')
        yield test_users
    finally:
        for user in test_users.values():
            user.destroy()

@pytest.fixture
def test_microposts(test_users):
    test_microposts = {}
    try:
        # 30個のmicropostをユーザーmichaelに登録
        fake = Faker()
        user = test_users['michael']
        for n in range(30):
            key = f'micropost_{n}'
            content = fake.text(max_nb_chars=50)
            m = user.microposts.create(content=content)
            if m:
                test_microposts[key] = m

        # microposts.ymlのmicropostを登録
        with open('tests/fixtures/microposts.yml') as f:
            data = yaml.safe_load(f)

        # registration orderの数値に従って並べ替えその順に登録する
        # most_recentが最後に登録されるようにする
        sorted_data = sorted(data.items(), key=lambda x:x[1]['registration_order'])
        for k,v in sorted_data:
            content=v['content']
            user_name = v['user']
            user = test_users[user_name]
            m = user.microposts.create(content=content)
            if m:
                test_microposts[k] = m

        yield test_microposts
    finally:
        # test後の削除はuserの削除から自動的に行われるのでここではやらない
        pass
