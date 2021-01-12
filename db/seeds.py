from sampleapp.models.user import User
from faker import Faker

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
                  admin=True)
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
                      password_confirmation=password)
    if not res:
        raise Exception(f'could not create "name" account')
