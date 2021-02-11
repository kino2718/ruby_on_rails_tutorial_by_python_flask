import pytest
from sampleapp.models.relationship import Relationship

@pytest.fixture
def relationship(test_users):
    relationship = Relationship(follower_id=test_users['michael'].id,
                                followed_id=test_users['archer'].id)
    return relationship

def test_should_be_valid(relationship):
    assert relationship.valid()

def test_should_require_a_follower_id(relationship):
    relationship.follower_id = None
    assert not relationship.valid()

def test_should_require_a_followed_id(relationship):
    relationship.followed_id = None
    assert not relationship.valid()
