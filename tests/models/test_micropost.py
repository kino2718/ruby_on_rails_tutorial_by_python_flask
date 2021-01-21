import pytest
from sampleapp.models.micropost import Micropost

@pytest.fixture
def micropost(test_users):
    user = test_users['michael']
    micropost = user.microposts.build(content='Lorem ipsum')
    return micropost

def test_should_be_valid(micropost):
    assert micropost.valid()

def test_user_id_should_be_present(micropost):
    micropost.user_id = None
    assert not micropost.valid()

def test_content_should_be_present(micropost):
    micropost.content = '   '
    assert not micropost.valid()

def test_content_should_be_at_most_140_characters(micropost):
    micropost.content = 'a' * 141
    assert not micropost.valid()

def test_order_should_be_most_recent_first(test_microposts):
    micropost = test_microposts['most_recent']
    first_micropost = Micropost.all()[0]
    assert micropost == first_micropost
