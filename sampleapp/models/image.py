from .errors import Errors
from google.cloud import datastore
from datetime import datetime, timezone
import copy

class Image:
    KIND_IMAGES = 'images'

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.micropost_id = kwargs.get('micropost_id')
        self.file_name = kwargs.get('file_name')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.errors = Errors()

    def __repr__(self):
        return f'Image(id={self.id.__repr__()}, ' +\
            f'micropost_id={self.micropost_id.__repr__()}, ' +\
            f'file_name={self.file_name.__repr__()}, ' +\
            f'created_at={self.created_at.__repr__()}, ' +\
            f'updated_at={self.updated_at.__repr__()})'

    def __str__(self):
        return f'Image(id={self.id}, ' +\
            f'micropost_id={self.micropost_id}, ' +\
            f'file_name={self.file_name}, ' +\
            f'created_at={self.created_at}, ' +\
            f'updated_at={self.updated_at})'

    def valid(self):
        self.errors = Errors()
        v = True
        if not self.micropost_id:
            v = False
            self.errors.add('micropost_id', "micropost_id can't be blank")
        if not self.file_name or not self.file_name.strip():
            v = False
            self.errors.add('file_name', "file_name can't be blank")
        if self.file_name and 255 < len(self.file_name):
            v = False
            self.errors.add('file_name', 'file_name is too long')
        return v


    def _insert_or_update(self):
        client = datastore.Client()
        if self.id:
            # update
            key = client.key(Image.KIND_IMAGES, self.id)
            image = client.get(key)
        else:
            # insert
            key = client.key(Image.KIND_IMAGES)
            image = datastore.Entity(key)

        image['micropost_id'] = self.micropost_id
        image['file_name'] = self.file_name
        t = datetime.now(timezone.utc)
        if not self.id:
            # insert
            image['created_at'] = t
        image['updated_at'] = t

        client.put(image)
        self.id = image.key.id
        self.created_at = image['created_at']
        self.updated_at = image['updated_at']
        return True

    def save(self):
        if not self.valid():
            return False
        return self._insert_or_update()

    @classmethod
    def create(cls, **kwargs):
        image = cls(**kwargs)
        image.save()
        return image

    def destroy(self):
        client = datastore.Client()
        key = client.key(Image.KIND_IMAGES, self.id)
        client.delete(key)

    @staticmethod
    def find_by(**kwargs):
        if not kwargs:
            return []
        client = datastore.Client()
        query = client.query(kind=Image.KIND_IMAGES)
        for k,v in kwargs.items():
            if k=='id':
                key = client.key(Image.KIND_IMAGES, v)
                query.key_filter(key, '=')
            else:
                query.add_filter(k, '=', v)
        entities = list(query.fetch())
        images = [Image(id=entity.key.id, **entity) for entity in entities]
        images.sort(key=lambda x: x.created_at, reverse=True)
        return images

    @staticmethod
    def all():
        client = datastore.Client()
        query = client.query(kind=Image.KIND_IMAGES)
        query.order = ['-created_at']
        entities = list(query.fetch())
        images = [Image(id=entity.key.id, **entity) for entity in entities]
        return images

    @staticmethod
    def count():
        return len(Image.all())
