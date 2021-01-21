from flask import current_app
from .errors import Errors
from google.cloud import datastore
from google.cloud import storage
from . import user
from datetime import datetime, timezone
import copy
from . import image as im
import os
from werkzeug.utils import secure_filename

class Micropost:
    KIND_MICROPOSTS = 'microposts'

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.content = kwargs.get('content')
        self.user_id = kwargs.get('user_id')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.errors = Errors()

    def __repr__(self):
        return f'Micropost(id={self.id.__repr__()}, ' +\
            f'content={self.content.__repr__()}, ' +\
            f'user_id={self.user_id.__repr__()}, ' +\
            f'created_at={self.created_at.__repr__()}, ' +\
            f'updated_at={self.updated_at.__repr__()})'

    def __str__(self):
        return f'Micropost(id={self.id}, ' +\
            f'content={self.content}, ' +\
            f'user_id={self.user_id}, ' +\
            f'created_at={self.created_at}, ' +\
            f'updated_at={self.updated_at})'

    def __eq__(self, other):
        if not isinstance(other, Micropost):
            return False
        # created_at, updated_atはdatetime.datetime型と
        # google.api_core.datetime_helpers.DatetimeWithNanoseconds型を
        # 取るので比較には用いない。手抜き
        return \
            self.id==other.id and \
            self.content==other.content and \
            self.user_id==other.user_id

    def valid(self):
        self.errors = Errors()
        v = True
        if not self.content or not self.content.strip():
            v = False
            self.errors.add('content', "content can't be blank")
        if self.content and 140 < len(self.content):
            v = False
            self.errors.add('content', 'content is too long')
        if not self.user_id:
            v = False
            self.errors.add('user_id', "user_id can't be blank")
        if not user.User.find(self.user_id):
            v = False
            self.errors.add('user', 'user must exist')
        if hasattr(self, 'image_file') and self.image_file:
            if self.image_file.mimetype not in \
               ['image/jpeg', 'image/gif', 'image/png']:
                v = False
                self.errors.add('image', 'file must be a valid image format')
            self.image_file.seek(0, os.SEEK_END)
            file_size = self.image_file.tell()
            self.image_file.seek(0, os.SEEK_SET)
            if 5*1024*1024 < file_size:
                v = False
                self.errors.add('image', 'file should be less than 5MB')
        return v

    def _insert_or_update(self):
        client = datastore.Client()
        if self.id:
            key = client.key(Micropost.KIND_MICROPOSTS, self.id)
            micropost = client.get(key)
        else:
            key = client.key(Micropost.KIND_MICROPOSTS)
            micropost = datastore.Entity(key)

        micropost['content'] = self.content
        micropost['user_id'] = self.user_id
        t = datetime.now(timezone.utc)
        if not self.id:
            # 新規登録
            micropost['created_at'] = t
        micropost['updated_at'] = t

        client.put(micropost)
        self.id = micropost.key.id
        self.created_at = micropost['created_at']
        self.updated_at = micropost['updated_at']
        return True

    def save(self):
        if not self.valid():
            return False
        ret = self._insert_or_update()
        if ret:
            self._save_attached_image()
        return ret

    @classmethod
    def create(cls, **kwargs):
        micropost = cls(**kwargs)
        micropost.save()
        return micropost

    def update(self, **kwargs):
        if len(kwargs) == 0:
            return True

        temp = copy.copy(self)
        dirty = False
        for k,v in kwargs.items():
            if k == 'content':
                if temp.content != v:
                    temp.content = v
                    dirty = False
            else:
                raise AttributeError(f'{k} key is bad')

        if not temp.valid():
            self.errors = temp.errors
            return False

        if dirty:
            if temp._insert_or_update():
                self.content = temp.content
                self.updated_at = temp.updated_at
                return True
            else:
                return False
        return True

    def update_columns(self, **kwargs):
        if len(kwargs) == 0:
            return True

        temp = copy.copy(self)
        dirty = False
        for k,v in kwargs.items():
            if k == 'content':
                if temp.content != v:
                    temp.content = v
                    dirty = True
            else:
                raise AttributeError(f'{k} key is bad')

        if dirty:
            if temp._insert_or_update():
                self.content = temp.content
                self.updated_at = temp.updated_at
                return True
            else:
                return False
        return True

    def update_attribute(self, k, v):
        return self.update_columns(**{k:v})

    def destroy(self):
        client = datastore.Client()
        key = client.key(Micropost.KIND_MICROPOSTS, self.id)
        client.delete(key)
        self._delete_attached_image()

    def reload(self):
        micropost = Micropost.find(self.id)
        self.content = micropost.content
        self.user_id = micropost.user_id
        self.created_at = micropost.created_at
        self.updated_at = micropost.updated_at
        self.errors = micropost.errors
        return self

    @staticmethod
    def find(id):
        if id is None:
            return None
        client = datastore.Client()
        key = client.key(Micropost.KIND_MICROPOSTS, id)
        entity = client.get(key)
        if entity is None:
            return None
        micropost = Micropost(id=entity.key.id, **entity)
        return micropost

    @staticmethod
    def find_by(**kwargs):
        if not kwargs:
            return []
        client = datastore.Client()
        query = client.query(kind=Micropost.KIND_MICROPOSTS)
        for k,v in kwargs.items():
            if k=='id':
                key = client.key(Micropost.KIND_MICROPOSTS, v)
                query.key_filter(key, '=')
            else:
                query.add_filter(k, '=', v)
        entities = list(query.fetch())
        microposts = [Micropost(id=entity.key.id, **entity) for entity in entities]
        microposts.sort(key=lambda x: x.created_at, reverse=True)
        return microposts

    @staticmethod
    def all():
        client = datastore.Client()
        query = client.query(kind=Micropost.KIND_MICROPOSTS)
        query.order = ['-created_at']
        entities = list(query.fetch())
        microposts = [Micropost(id=entity.key.id, **entity) for entity in entities]
        return microposts

    @staticmethod
    def count():
        return len(Micropost.all())

    def user(self):
        return user.User.find(self.user_id)

    def image_attach(self, image_file):
        self.image_file = image_file

    def image_attached(self):
        images = im.Image.find_by(micropost_id=self.id)
        if images:
            return True
        else:
            return False

    def image_url(self):
        images = im.Image.find_by(micropost_id=self.id)
        if images:
            image = images[0]
            client = storage.Client()
            bucket = client.get_bucket(current_app.config['BUCKET_IMAGES'])
            blob_name = f'{self.id}/{image.file_name}'
            blob = bucket.get_blob(blob_name)
            if blob:
                return blob.public_url
        return None

    def _save_attached_image(self):
        if hasattr(self, 'image_file') and self.image_file:
            # Cloud Storageに保存するので必要無いはずだが念の為
            file_name = secure_filename(self.image_file.filename)
            if file_name:
                image = im.Image(micropost_id=self.id, file_name=file_name)
                if image.save():
                    client = storage.Client()
                    bucket = client.get_bucket(current_app.config['BUCKET_IMAGES'])
                    blob_name = f'{self.id}/{file_name}'
                    blob = bucket.blob(blob_name)
                    blob.upload_from_file(self.image_file,
                                          content_type=self.image_file.mimetype)

    def _delete_attached_image(self):
        for image in im.Image.find_by(micropost_id=self.id):
            image.destroy()
            client = storage.Client()
            bucket = client.get_bucket(current_app.config['BUCKET_IMAGES'])
            blob_name = f'{self.id}/{image.file_name}'
            bucket.delete_blob(blob_name)
