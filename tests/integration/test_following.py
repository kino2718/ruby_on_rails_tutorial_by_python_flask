from common import log_in_as
import re

def test_following_page(client, test_users, test_relationships):
    user = test_users['michael']
    with client:
        log_in_as(client, user.email)
        response = client.get(f'/users/{user.id}/following')
        contents = response.data.decode(encoding='utf-8')
        following = user.following()
        assert following
        assert re.search(f'{len(following)}', contents)
        for u in following:
            assert re.search(f'<a href="/users/{u.id}"', contents)

def test_followers_page(client, test_users, test_relationships):
    user = test_users['michael']
    with client:
        log_in_as(client, user.email)
        response = client.get(f'/users/{user.id}/followers')
        contents = response.data.decode(encoding='utf-8')
        followers = user.followers()
        assert followers
        assert re.search(f'{len(followers)}', contents)
        for u in followers:
            assert re.search(f'<a href="/users/{u.id}"', contents)

def test_should_follow_a_user_the_standard_way(client, test_users):
    user = test_users['michael']
    other = test_users['archer']
    with client:
        log_in_as(client, user.email)
        before_count = len(user.following())
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        response = client.post(
            '/relationships',
            data={
                'followed_id': other.id,
                'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = len(user.following())
        assert before_count+1 == after_count

def test_should_follow_a_user_with_Ajax(client, test_users):
    user = test_users['michael']
    other = test_users['archer']
    with client:
        log_in_as(client, user.email)
        before_count = len(user.following())
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        response = client.post(
            '/relationships',
            data={
                'followed_id': other.id,
                'authenticity_token': token},
            headers={'accept': 'application/json'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = len(user.following())
        assert before_count+1 == after_count

def test_should_unfollow_a_user_the_standard_way(client, test_users):
    user = test_users['michael']
    other = test_users['archer']
    user.follow(other)
    relationship = user.active_relationships_find_by(other.id)
    with client:
        log_in_as(client, user.email)
        before_count = len(user.following())
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        response = client.post(
            f'/relationships/{relationship.id}',
            data={
                '_method': 'delete',
                'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = len(user.following())
        assert before_count-1 == after_count

def test_should_unfollow_a_user_with_Ajax(client, test_users):
    user = test_users['michael']
    other = test_users['archer']
    user.follow(other)
    relationship = user.active_relationships_find_by(other.id)
    with client:
        log_in_as(client, user.email)
        before_count = len(user.following())
        # csrf tokenをsessionに設定する
        token = 'token'
        with client.session_transaction() as sess:
            sess['csrf_token'] = token
        response = client.post(
            f'/relationships/{relationship.id}',
            data={
                '_method': 'delete',
                'authenticity_token': token},
            headers={'accept': 'application/json'},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        after_count = len(user.following())
        assert before_count-1 == after_count
