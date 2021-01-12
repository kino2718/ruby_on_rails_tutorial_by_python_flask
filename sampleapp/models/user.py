from google.cloud import datastore
from google.api_core.exceptions import Aborted
from datetime import datetime
import copy
import re
from werkzeug.security import check_password_hash, generate_password_hash
from .errors import Errors
import secrets

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
        self.remember_token = kwargs.get('remember_token')
        self.remember_digest = kwargs.get('remember_digest')
        self.admin = kwargs.get('admin', False)
        self.errors = Errors()

    def __repr__(self):
        return f'User(id={self.id.__repr__()}, ' +\
            f'name={self.name.__repr__()}, email={self.email.__repr__()}, ' +\
            f'created_at={self.created_at.__repr__()}, ' +\
            f'updated_at={self.updated_at.__repr__()}, ' +\
            f'password={self.password.__repr__()}, ' +\
            f'password_confirmation={self.password_confirmation.__repr__()}, ' +\
            f'password_digest={self.password_digest.__repr__()}, ' +\
            f'remember_token={self.remember_token.__repr__()}, ' +\
            f'remember_digest={self.remember_digest.__repr__()}, ' +\
            f'admin={self.admin.__repr__()})'

    def __str__(self):
        return f'User(id={self.id}, name={self.name}, email={self.email}, ' +\
            f'created_at={self.created_at}, ' +\
            f'updated_at={self.updated_at}, ' +\
            f'password={self.password}, ' +\
            f'password_confirmation={self.password_confirmation}, ' +\
            f'password_digest={self.password_digest}, ' +\
            f'remember_token={self.remember_token}, ' +\
            f'remember_digest={self.remember_digest}, ' +\
            f'admin={self.admin})'

    def __eq__(self, other):
        # created_at, updated_atはdatetime.datetime型と
        # google.api_core.datetime_helpers.DatetimeWithNanoseconds型を
        # 取るので比較には用いない。手抜き
        return \
            self.id==other.id and \
            self.name==other.name and \
            self.email==other.email and \
            self.password_digest==other.password_digest and \
            self.remember_digest==other.remember_digest and \
            self.admin==other.admin

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

        good_password = True
        if self.id:
            # 既存ユーザー。passwordブランクは許されるので
            # passwordに値が入っている場合のみチェック
            if self.password:
                if not self.password.strip():
                    # passwordが全て空白
                    good_password = False
                    v = False
                    self.errors.add('password', "password can't be blank")
                else:
                    if len(self.password) < 6:
                        # passwordの長さが6文字未満
                        good_password = False
                        v = False
                        self.errors.add('password', 'password is too short')
        else:
            # 新規ユーザー
            if not self.password or not self.password.strip():
                # passwordが空又はNone又は全て空白
                good_password = False
                v = False
                self.errors.add('password', "password can't be blank")
            else:
                if len(self.password) < 6:
                    # passwordの長さが文字未満
                    good_password = False
                    v = False
                    self.errors.add('password', 'password is too short')

        if good_password and self.password != self.password_confirmation:
            v = False
            self.errors.add('password_confirmation', "password confirmation doesn't match password")

        # if not v:
        #     print(f'Invalid: {self}. {self.errors}')
        return v

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

    def _insert_or_update_user(self, client, user):
        t = datetime.utcnow()
        user['name'] =  self.name
        user['email'] = self.email
        if not self.id:
            #新規登録
            user['created_at'] = t
        user['updated_at'] = t
        user['password_digest'] = self.password_digest
        user['remember_digest'] = self.remember_digest
        user['admin'] = self.admin

        client.put(user)
        self.created_at = user['created_at']
        self.updated_at = user['updated_at']
        return user

    def _insert(self):
        client = datastore.Client()
        try:
            with client.transaction():
                email_key = client.key(User.KIND_EMAILS, self.email)
                user_key = client.key(User.KIND_USERS)
                user = datastore.Entity(user_key)
                if self._check_email_unique_and_insert(client, email_key):
                    user = self._insert_or_update_user(client, user)
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
                        self._insert_or_update_user(client, user)
            except Aborted as e:
                # transaction競合のため失敗
                # print(f'{self.name}: 例外発生: {type(e)} {e}')
                # print(f'{self.name}: ユーザー更新失敗')
                return False
        else:
            # print('update: メールアドレスが同じ')
            self._insert_or_update_user(client, user)
        return True

    def save(self):
        # email を小文字に変換する
        if self.email is not None:
            self.email = self.email.lower()

        # user属性の有効性をチェックする
        if not self.valid():
            return False

        # password_digest を作成
        self.password_digest = User.digest(self.password)

        # idが存在する時はupdate、存在しない時はinsertを行う
        if self.id:
            return self._update()
        else:
            return self._insert()

    def update(self, **kwargs):
        # remember_token, remember_digestはここでは扱わずrememberメソッドで扱う
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
                # email を小文字に変換する
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
            elif k == 'admin':
                if temp.admin != v:
                    temp.admin = v
                    dirty = True
            else:
                raise AttributeError(f'{k} key is bad')

        # 変更する属性の有効性をチェックする
        if not temp.valid():
            self.errors = temp.errors
            return False

        if dirty:
            # password_digest を作成。passwordがFalseの時は以前のままにする
            if self.password:
                temp.password_digest = User.digest(temp.password)
            if temp._update():
                self.name = temp.name
                self.email = temp.email
                self.updated_at = temp.updated_at
                self.password = temp.password
                self.password_confirmation = temp.password_confirmation
                self.password_digest = temp.password_digest
                self.admin = temp.admin
                return True
        return False

    def update_attribute(self, **kwargs):
        if len(kwargs) == 0:
            return True

        temp = copy.copy(self)
        dirty = False
        for k,v in kwargs.items():
            if k == 'name':
                if temp.name != v:
                    temp.name = v
                    dirty = True
            elif k == 'email':
                # email を小文字に変換する
                if temp.email.lower() != v.lower():
                    temp.email = v.lower()
                    dirty = True
            elif k == 'password_digest':
                if temp.password_digest != v:
                    temp.password_digest = v
                    dirty = True
            elif k == 'remember_digest':
                if temp.remember_digest != v:
                    temp.remember_digest = v
                    dirty = True
            elif k == 'admin':
                if temp.admin != v:
                    temp.admin = v
                    dirty = True
            else:
                raise AttributeError(f'{k} key is bad')

        if dirty:
            if temp._update():
                self.name = temp.name
                self.email = temp.email
                self.updated_at = temp.updated_at
                self.password_digest = temp.password_digest
                self.remember_digest = temp.remember_digest
                self.admin = temp.admin
                return True
        return False

    @classmethod
    def create(cls, **kwargs):
        user = cls(**kwargs)
        user.save()
        return user

    def reload(self):
        user = User.find(self.id)
        self.name = user.name
        self.email = user.email
        self.created_at = user.created_at
        self.updated_at = user.updated_at
        self.password = user.password
        self.password_confirmation = user.password_confirmation
        self.password_digest = user.password_digest
        self.remember_token = user.remember_token
        self.remember_digest = user.remember_digest
        self.admin = user.admin
        self.errors = user.errors
        return self

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
        if id is None:
            return None
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
        query.order = ['created_at']
        entities = list(query.fetch())
        users = [User(id=entity.key.id, **entity) for entity in entities]
        return users

    @staticmethod
    def paginate(page=None):
        if page is None:
            page = 1
        elif page < 1:
            raise IndexError('paginate: page must be greater than or equal to 1')
        limit = 30
        offset = (page-1)*limit
        client = datastore.Client()
        query = client.query(kind=User.KIND_USERS)
        query.order = ['created_at']
        entities = list(query.fetch(limit=limit, offset=offset))
        users = [User(id=entity.key.id, **entity) for entity in entities]
        return users

    @staticmethod
    def count():
        # 統計情報はリアルタイムで反映されないので使用できない
        # client = datastore.Client()
        # key = client.key('__Stat_Kind__', 'emails')
        # entity = client.get(key)
        # if entity is not None:
        #     count = entity.get('count')
        #     if count is not None:
        #         return count
        users = User.all()
        return len(users)

    def authenticate(self, p):
        if check_password_hash(self.password_digest, p):
            return self
        return None

    def authenticated_by_remember_token(self, remember_token):
        if not self.remember_digest:
            return False
        return check_password_hash(self.remember_digest, remember_token)

    @staticmethod
    def digest(string):
        return generate_password_hash(string)

    @staticmethod
    def new_token():
        token = secrets.token_urlsafe()
        return token

    def remember(self):
        self.remember_token = User.new_token()
        digest = User.digest(self.remember_token)
        self.update_attribute(remember_digest=digest)

    def forget(self):
        self.update_attribute(remember_digest=None)

    def _does_email_exist(self):
        client = datastore.Client()
        users = self.find_by('email', self.email)
        if len(users) == 0 or users[0].id == self.id:
            return False
        return True
