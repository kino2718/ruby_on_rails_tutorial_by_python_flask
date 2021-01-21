from sampleapp.models.user import User
from faker import Faker
from datetime import datetime, timezone

# 最初に全てのユーザーを削除する
print('**** delete all users ****')
for user in User.all():
    user.destroy()

# メインのサンプルユーザーを1人作成する
print('**** add main user ****')
res = User.create(name="Example User",
                  email="example@railstutorial.org",
                  password="foobar",
                  password_confirmation="foobar",
                  admin=True,
                  activated=True,
                  activated_at=datetime.now(timezone.utc))
if not res:
    raise Exception('could not create main user account')

# 追加のユーザーをまとめて生成する
print('**** add aditional users ****')
fake = Faker()
for n in range(99):
    name  = fake.name()
    print(f'add "{name}"')
    email = f'example-{n+1}@railstutorial.org'
    password = "password"
    res = User.create(name=name,
                      email=email,
                      password=password,
                      password_confirmation=password,
                      activated=True,
                      activated_at=datetime.now(timezone.utc))
    if not res:
        raise Exception(f'could not create "name" account')

# ユーザーの一部を対象にマイクロポストを生成する
print('**** add microposts ****')
users = User.all()
users.sort(key=lambda x: x.created_at)
users = users[:6]

for n in range(50):
    content = fake.text(max_nb_chars=50)
    print(f'add content: {content}')
    for user in users:
        user.microposts.create(content=content)
