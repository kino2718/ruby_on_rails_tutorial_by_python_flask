from .errors import Errors
from google.cloud import datastore
from datetime import datetime, timezone
import copy
from . import user

class Relationship:
    KIND_RELATIONSHIPS = 'relationships'

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.follower_id = kwargs.get('follower_id')
        self.followed_id = kwargs.get('followed_id')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.errors = Errors()

    def __repr__(self):
        return f'Relationship(id={self.id!r}, ' +\
            f'follower_id={self.follower_id!r}, ' +\
            f'followed_id={self.followed_id!r}, ' +\
            f'created_at={self.created_at!r}, ' +\
            f'updated_at={self.updated_at!r})'

    def __str__(self):
        return f'Relationship(id={self.id}, ' +\
            f'follower_id={self.follower_id}, ' +\
            f'followed_id={self.followed_id}, ' +\
            f'created_at={self.created_at}, ' +\
            f'updated_at={self.updated_at})'

    def valid(self):
        self.errors = Errors()
        v = True
        if not self.follower_id:
            v = False
            self.errors.add('follower_id', "follower_id can't be blank")
        if not self.followed_id:
            v = False
            self.errors.add('followed_id', "followed_id can't be blank")
        if Relationship.find_by(follower_id=self.follower_id,
                                followed_id=self.followed_id):
            # multi threadで同時に同じrelationshipを保存した場合、
            # 同じrelationshipが複数存在してしまう問題がある。
            # 万一そうなった場合はそれでも良いデータなので厳密にunique
            # にすることはしない。destroy時に対策をする。
            v = False
            self.errors.add('', "same relationship can't exist")
        if self.follower_id == self.followed_id:
            v = False
            self.errors.add('', "follower_id and followed_id can't be same")
        return v

    def _insert_or_update(self):
        client = datastore.Client()
        if self.id:
            key = client.key(Relationship.KIND_RELATIONSHIPS, self.id)
            relationship = client.get(key)
        else:
            key = client.key(Relationship.KIND_RELATIONSHIPS)
            relationship = datastore.Entity(key)

        relationship['follower_id'] = self.follower_id
        relationship['followed_id'] = self.followed_id
        t = datetime.now(timezone.utc)
        if not self.id:
            relationship['created_at'] = t
        relationship['updated_at'] = t

        client.put(relationship)
        self.id = relationship.key.id
        self.created_at = relationship['created_at']
        self.updated_at = relationship['updated_at']
        return True

    def save(self):
        if not self.valid():
            return False
        return self._insert_or_update()

    @classmethod
    def create(cls, **kwargs):
        relationship = cls(**kwargs)
        relationship.save()
        return relationship

    def destroy(self):
        client = datastore.Client()
        key = client.key(Relationship.KIND_RELATIONSHIPS, self.id)
        client.delete(key)

    @staticmethod
    def find(id):
        if id is None:
            return None
        client = datastore.Client()
        key = client.key(Relationship.KIND_RELATIONSHIPS, id)
        entity = client.get(key)
        if entity is None:
            return None
        relationship = Relationship(id=entity.key.id, **entity)
        return relationship

    @staticmethod
    def find_by(**kwargs):
        if not kwargs:
            return []
        client = datastore.Client()
        query = client.query(kind=Relationship.KIND_RELATIONSHIPS)
        for k,v in kwargs.items():
            if k=='id':
                key = client.key(Relationship.KIND_RELATIONSHIPS, v)
                query.key_filter(key, '=')
            else:
                query.add_filter(k, '=', v)
        entities = list(query.fetch())
        relationships = [Relationship(id=entity.key.id, **entity)
                         for entity in entities]
        return relationships

    @staticmethod
    def all():
        client = datastore.Client()
        query = client.query(kind=Relationship.KIND_RELATIONSHIPS)
        entities = list(query.fetch())
        relationships = [Relationship(id=entity.key.id, **entity)
                         for entity in entities]
        return relationships

    @staticmethod
    def count():
        return len(Relationship.all())

    def follower(self):
        return user.User.find(self.follower_id)

    def followed(self):
        return user.User.find(self.followed_id)
