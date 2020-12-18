from google.cloud import datastore
from google.api_core.exceptions import Aborted
from datetime import datetime
import copy
import re
from werkzeug.security import check_password_hash, generate_password_hash
from .errors import Errors

class User:
    KIND_EMAILS = 'emails'
    KIND_USERS = 'users'
    EMAIL_PATTERN = re.compile(r'\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\Z',
                               flags=re.IGNORECASE)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.password = kwargs.get('password')
        self.password_confirmation = kwargs.get('password_confirmation')
        self.password_digest = kwargs.get('password_digest')
        self.errors = Errors()

    def __repr__(self):
        return f'User(id={self.id.__repr__()}, ' +\
            f'name={self.name.__repr__()}, email={self.email.__repr__()}, ' +\
            f'created_at={self.created_at.__repr__()}, ' +\
            f'updated_at={self.updated_at.__repr__()}, ' +\
            f'password={self.password.__repr__()}, ' +\
            f'password_confirmation={self.password_confirmation.__repr__()}, ' +\
            f'password_digest={self.password_digest.__repr__()})'

    def __str__(self):
        return f'User(id={self.id}, name={self.name}, email={self.email}, ' +\
            f'created_at={self.created_at}, ' +\
            f'updated_at={self.updated_at}, ' +\
            f'password={self.password}, ' +\
            f'password_confirmation={self.password_confirmation}, ' +\
            f'password_digest={self.password_digest})'

    def valid(self):
        self.errors = Errors()
        v = True
        if (not self.name) or (not self.name.strip()):
            v = False
            self.errors.add('name', "name can't be blank")
        if self.name and (50 < len(self.name)):
            v = False
            self.errors.add('name', "name is too long")
        if (not self.email) or (not self.email.strip()):
            v = False
            self.errors.add('email', "email can't be blank")
        if self.email and (255 < len(self.email)):
            v = False
            self.errors.add('email', 'email is too long')
        if self.email and (not User.EMAIL_PATTERN.match(self.email)):
            v = False
            self.errors.add('email', 'email is invalid')
        if self._does_email_exist():
            v = False
            self.errors.add('email', 'email has already been taken')
        if (not self.password) or (not self.password.strip()):
            v = False
            self.errors.add('password', "password can't be blank")
        if self.password and (len(self.password) < 6):
            v = False
            self.errors.add('password', 'password is too short')
        if self.password != self.password_confirmation:
            v = False
            self.errors.add('password_confirmation', "password confirmation doesn't match password")

        # if not v:
        #     print(f'Invalid: {self}. {self.errors}')
        return v

    # decorator
    def _must_be_valid(f):
        def wrapper(self, *args, **kwargs):
            if not self.valid():
                return False
            return f(self, *args, **kwargs)
        return wrapper

    # decorator
    def _email_to_lower(f):
        def wrapper(self, *args, **kwargs):
            self.email = self.email.lower()
            return f(self, *args, **kwargs)
        return wrapper

    def _check_email_unique_and_insert(self, client, key):
        # print(f'{self.name}: {self.email}登録開始')
        # emailアドレスが既に登録されているか確認
        entity = client.get(key)
        # print(f'{self.name}: メール登録済みかを確認')
        if entity is not None:
            # 既に登録済み
            # print(f'{self.name}: {self.email}は既に使用されている')
            return False

        # emailアドレスを登録
        entity = datastore.Entity(key=key)
        entity['created_at'] = datetime.utcnow()
        # print(f'{self.name}: メール登録開始')
        client.put(entity)
        return True

    def _insert_user(self, client, key):
        # print(f'{self.name}: ユーザー登録開始')
        user = datastore.Entity(key)
        t = datetime.utcnow()
        # password_digest を作成
        digest = generate_password_hash(self.password)
        user.update({
            'name': self.name,
            'email': self.email,
            'created_at': t,
            'updated_at': t,
            'password_digest': digest
        })
        client.put(user)
        self.created_at = user['created_at']
        self.updated_at = user['updated_at']
        self.password_digest = user['password_digest']
        return user

    def _update_user(self, client, user):
        # print(f'{self.name}: ユーザー登録更新')
        t = datetime.utcnow()
        # password_digest を作成
        digest = generate_password_hash(self.password)
        user.update({
            'name': self.name,
            'email': self.email,
            'updated_at': t,
            'password_digest': digest
        })
        client.put(user)
        self.updated_at = user['updated_at']
        self.password_digest = user['password_digest']
        return user

    @_email_to_lower
    @_must_be_valid
    def _insert(self):
        client = datastore.Client()
        email_key = client.key(User.KIND_EMAILS, self.email)
        user_key = client.key(User.KIND_USERS)
        user = None
        try:
            with client.transaction():
                if self._check_email_unique_and_insert(client, email_key):
                    user = self._insert_user(client, user_key)
        except Aborted as e:
            # transaction競合のため失敗
            # print(f'{self.name}: 例外発生: {type(e)} {e}')
            # print(f'{self.name}: ユーザー登録失敗')
            return False

        # transactionの外で行うこと
        if user:
            self.id = user.key.id

        # print(f'{self.name}: ユーザー登録終了')
        return True

    @_email_to_lower
    @_must_be_valid
    def _update(self):
        client = datastore.Client()
        user_key = client.key(User.KIND_USERS, self.id)
        user = client.get(user_key)
        if self.email != user['email']:
            # print('update: メールアドレスが違う')
            email_key = client.key(User.KIND_EMAILS, user['email'])
            try:
                with client.transaction():
                    # メールアドレスを削除
                    client.delete(email_key)
                    # 新しいメールアドレスをチェックしてユーザー情報をアップデート
                    email_key = client.key(User.KIND_EMAILS, self.email)
                    if self._check_email_unique_and_insert(client, email_key):
                        self._update_user(client, user)
            except Aborted as e:
                # transaction競合のため失敗
                # print(f'{self.name}: 例外発生: {type(e)} {e}')
                # print(f'{self.name}: ユーザー更新失敗')
                return False
        else:
            # print('update: メールアドレスが同じ')
            self._update_user(client, user)
        return True

    def save(self):
        # idが存在する時はupdate、存在しない時はinsertを行う
        if self.id:
            return self._update()
        else:
            return self._insert()

    def update(self, **kwargs):
        if len(kwargs) == 0:
            # print(f'test update: no update values')
            return True

        temp = copy.copy(self)
        dirty = False
        for k,v in kwargs.items():
            if k == 'name':
                if temp.name != v:
                    temp.name = v
                    dirty = True
            elif k == 'email':
                if temp.email.lower() != v.lower():
                    temp.email = v.lower()
                    dirty = True
            elif k == 'password':
                if temp.password != v:
                    temp.password = v
                    dirty = True
            elif k == 'password_confirmation':
                if temp.password_confirmation != v:
                    temp.password_confirmation = v
                    dirty = True
            else:
                raise AttributeError(f'{k} key is bad')

        if dirty:
            if temp._update():
                self.name = temp.name
                self.email = temp.email
                self.updated_at = temp.updated_at
                self.password = temp.password
                self.password_confirmation = temp.password_confirmation
                self.password_digest = temp.password_digest
                return True
            else:
                self.errors = temp.errors
        return False

    @classmethod
    def create(cls, **kwargs):
        user = cls(**kwargs)
        user.save()
        return user

    def destroy(self):
        client = datastore.Client()
        email_key = client.key(User.KIND_EMAILS, self.email)
        user_key = client.key(User.KIND_USERS, self.id)
        with client.transaction():
            client.delete(email_key)
            client.delete(user_key)
        return self

    @staticmethod
    def find(id):
        client = datastore.Client()
        key = client.key(User.KIND_USERS, id)
        entity = client.get(key)
        if entity is None:
            return None
        user = User(id=entity.key.id, **entity)
        return user

    @staticmethod
    def find_by(type, value):
        if value is None:
            return []
        if type == 'email':
            value = value.lower()
        client = datastore.Client()
        query = client.query(kind=User.KIND_USERS)
        query.add_filter(type, '=', value)
        entities = list(query.fetch())
        users = [User(id=entity.key.id, **entity) for entity in entities]
        return users

    @staticmethod
    def all():
        client = datastore.Client()
        query = client.query(kind=User.KIND_USERS)
        entities = list(query.fetch())
        users = [User(id=entity.key.id, **entity) for entity in entities]
        return users

    @staticmethod
    def count():
        users = User.all()
        return len(users)

    def authenticate(self, p):
        if check_password_hash(self.password_digest, p):
            return self
        return None

    def _does_email_exist(self):
        client = datastore.Client()
        users = self.find_by('email', self.email)
        if len(users) == 0 or users[0].id == self.id:
            return False
        return True
