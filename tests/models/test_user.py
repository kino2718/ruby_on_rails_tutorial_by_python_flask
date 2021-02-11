import pytest
import copy
from sampleapp.models.user import User
from sampleapp.models.micropost import Micropost

@pytest.fixture
def user():
    user = User(name='Example User', email='user@example.com',
                password='foobar', password_confirmation='foobar')
    return user

def test_should_be_valid(user):
    assert user.valid()

def test_name_should_be_present(user):
    user.name = "     "
    assert not user.valid()

def test_email_should_be_present(user):
    user.email = "     "
    assert not user.valid()

def test_name_should_not_be_too_long(user):
    user.name = "a" * 51
    assert not user.valid()

def test_email_should_not_be_too_long(user):
    user.email = "a" * 244 + "@example.com"
    assert not user.valid()

def test_email_validation_should_accept_valid_addresses(user):
    valid_addresses = ["user@example.com", "USER@foo.COM",
                       "A_US-ER@foo.bar.org", "first.last@foo.jp",
                       "alice+bob@baz.cn"]

    for valid_address in valid_addresses:
        user.email = valid_address
        assert user.valid(), f"{valid_address} should be valid"

def test_email_validation_should_reject_invalid_addresses(user):
    invalid_addresses = ["user@example,com", "user_at_foo.org",
                         "user.name@example.", "foo@bar_baz.com",
                         "foo@bar+baz.com"]
    for invalid_address in invalid_addresses:
        user.email = invalid_address
        assert not user.valid(), f"{invalid_address} should be invalid"

def test_email_addresses_should_be_unique(user):
    try:
        duplicate_user = copy.copy(user)
        user.save()
        assert not duplicate_user.valid()
    finally:
        user.destroy()

def test_password_should_be_present_nonblank(user):
    user.password = user.password_confirmation = " " * 6
    assert not user.valid()

def test_password_should_have_a_minimum_length(user):
    user.password = user.password_confirmation = "a" * 5
    assert not user.valid()

def test_authenticated_should_return_false_for_a_user_with_nil_digest(user):
    assert not user.authenticated('remember', '')

def test_associated_microposts_should_be_destroyed(user):
    try:
        user.save()
        m = user.microposts.create(content="Lorem ipsum")
        before_count = Micropost.count()
    finally:
        user.destroy()
        after_count = Micropost.count()
        m = Micropost.find(m.id)
        if m:
            m.destroy()
        assert before_count - 1 == after_count

def test_should_follow_and_unfollow_a_user(test_users):
    michael = test_users['michael']
    archer = test_users['archer']
    assert not michael.is_following(archer)
    michael.follow(archer)
    assert michael.is_following(archer)
    assert michael in archer.followers()
    michael.unfollow(archer)
    assert not michael.is_following(archer)

def test_feed_should_have_the_right_posts(test_users, test_microposts,
                                          test_relationships):
    michael = test_users['michael']
    archer  = test_users['archer']
    lana    = test_users['lana']
    # フォローしているユーザーの投稿を確認
    for post_following in lana.microposts():
        assert post_following in michael.feed()
    # 自分自身の投稿を確認
    for post_self in michael.microposts():
        assert post_self in michael.feed()
    # フォローしていないユーザーの投稿を確認
    for post_unfollowed in archer.microposts():
        assert not post_unfollowed in michael.feed()
