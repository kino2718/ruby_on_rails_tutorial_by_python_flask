import pytest
from sampleapp.models.user import User

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

import copy
def test_email_addresses_should_be_unique(user):
    duplicate_user = copy.copy(user)
    #duplicate_user.email = user.email.upper()
    user.save()
    try:
        assert not duplicate_user.valid()
    finally:
        user.destroy()

def test_password_should_be_present_nonblank(user):
    user.password = user.password_confirmation = " " * 6
    assert not user.valid()

def test_password_should_have_a_minimum_length(user):
    user.password = user.password_confirmation = "a" * 5
    assert not user.valid()
