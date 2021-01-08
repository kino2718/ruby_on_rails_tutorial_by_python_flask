from flask import render_template, get_flashed_messages
from common import AUTHENTICITY_TOKEN_PATTERN, are_same_templates, log_in_as
from sampleapp.models.user import User

def test_unsuccessful_edit(client, test_users):
    user = test_users['michael']
    with client:
        # ログインする
        log_in_as(client, user.email)

        # 編集ページにアクセス
        response = client.get(f'/users/{user.id}/edit')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        # 編集ページが表示されたことを確認
        ref = render_template('users/edit.html', user=user, csrf_token=token)
        assert are_same_templates(ref, contents)
        # 無効な編集を行う
        response = client.post(
            f'/users/{user.id}',
            data={'_method': 'patch',
                  'name': '',
                  'email': 'foo@invalid',
                  'password': 'foo',
                  'password_confirmation': 'bar',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        # エラーメッセージを表示させるためuserをupdateし失敗させる
        user.update(name='', email='foo@invalid',
                    password='foo', password_confirmation='bar')
        # 編集に失敗し編集ページに戻されたことを確認
        ref = render_template('users/edit.html', user=user, csrf_token=token)
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)

def test_successful_edit(client, test_users):
    user = test_users['michael']
    with client:
        # ログインする
        log_in_as(client, user.email)

        # 編集ページアクセス
        response = client.get(f'/users/{user.id}/edit')
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]
        # 編集ページが表示されたことを確認
        ref = render_template('users/edit.html', user=user, csrf_token=token)
        assert are_same_templates(ref, contents)

        # 有効な編集を行う。
        name = 'Foo Bar'
        email = 'foo@bar.com'
        response = client.post(
            f'/users/{user.id}',
            data={'_method': 'patch',
                  'name': name,
                  'email': email,
                  'password': '',
                  'password_confirmation': '',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')
        # m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        # assert len(m.groups()) == 1
        # token = m.groups()[0]

        # flashメッセージが存在することを確認
        flashed_message = get_flashed_messages()
        assert flashed_message

        user.reload()
        assert name == user.name
        assert email == user.email

        # redirectされていることを確認
        ref = render_template('users/show.html', user=user)
        contents = response.data.decode(encoding='utf-8')
        assert are_same_templates(ref, contents)

def test_successful_edit_with_friendly_forwarding(client, test_users):
    user = test_users['michael']
    with client:
        # 編集ページアクセス
        client.get(f'/users/{user.id}/edit')

        # ログインする
        response = log_in_as(client, user.email)
        contents = response.data.decode(encoding='utf-8')
        m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
        assert len(m.groups()) == 1
        token = m.groups()[0]

        # 編集ページが表示されたことを確認
        ref = render_template('users/edit.html', user=user, csrf_token='')
        #print(f'\nref:\n{ref}\n\ncontents\n{contents}\n')
        assert are_same_templates(ref, contents)

        # 有効な編集を行う。
        name = 'Foo Bar'
        email = 'foo@bar.com'
        response = client.post(
            f'/users/{user.id}',
            data={'_method': 'patch',
                  'name': name,
                  'email': email,
                  'password': '',
                  'password_confirmation': '',
                  'authenticity_token': token},
            follow_redirects=True)
        contents = response.data.decode(encoding='utf-8')

        # flashメッセージが存在することを確認
        flashed_message = get_flashed_messages()
        assert flashed_message

        user.reload()
        assert name == user.name
        assert email == user.email
