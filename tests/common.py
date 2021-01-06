from flask import render_template, session
import re

AUTHENTICITY_TOKEN_PATTERN = re.compile(r'name="authenticity_token" value="(.*)"')
META_TAG_AUTHENTICITY_TOKEN_PATTERN = re.compile(r'name="csrf-token" content="(.*)"')

def is_logged_in():
    return session.get('id')

def are_same_templates(ref, contents):
    # meta tagのcsrf-tokenを取り除く
    ref = re.sub(r'<meta name="csrf-token" content=".*" />', r'', ref)
    contents = re.sub(r'<meta name="csrf-token" content=".*" />', r'', contents)
    # formのcsrf-tokenを取り除く
    ref = re.sub(r'<input .*name="authenticity_token" value=".*" />', r'', ref)
    contents = re.sub(r'<input .*name="authenticity_token" value=".*" />', r'',
                      contents)
    return ref == contents

def log_in_as(client, email, password='password', remember_me='1'):
    # ログインページの表示
    response = client.get('/login')
    contents = response.data.decode(encoding='utf-8')
    m = AUTHENTICITY_TOKEN_PATTERN.search(contents)
    assert len(m.groups()) == 1
    token = m.groups()[0]

    # ログインページが表示されたことを確認
    ref = render_template('sessions/new.html', csrf_token=token)
    assert are_same_templates(ref, contents)

    # ログインを行う
    if remember_me == '1':
        response = client.post(
            '/login', data={'email': email,
                            'password': password,
                            'remember_me': remember_me,
                            'authenticity_token': token},
            follow_redirects=True)
    else:
        # Ruby on Rails Tutorialと異なりremember me checkboxがチェックされていない
        # 時はパラメータは存在しない
        response = client.post(
            '/login', data={'email': email,
                            'password': password,
                            'authenticity_token': token},
            follow_redirects=True)

    return response

def log_out(client, current_contents):
    # meta tagのcsrf tokenを取得
    m = META_TAG_AUTHENTICITY_TOKEN_PATTERN.search(current_contents)
    assert len(m.groups()) == 1
    token = m.groups()[0]
    session['csrf_token_meta_tag'] = token
    response = client.post(
        '/logout',
        data = {
            '_method': 'delete',
            'authenticity_token': token
        },
        follow_redirects=True)
    return response
