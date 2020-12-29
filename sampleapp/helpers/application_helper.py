from flask import session, request
import secrets

_CSRF_TOKEN = 'csrf_token'
_CSRF_TOKEN_META_TAG = 'csrf_token_meta_tag'
_AUTHENTICITY_TOKEN = 'authenticity_token'

def full_title(page_title = ''):
    base_title = 'Ruby on Rails Tutorial Sample App'
    if not page_title:
        return base_title
    else:
        return f'{page_title} | {base_title}'

def csrf_token():
    token = secrets.token_urlsafe()
    session[_CSRF_TOKEN] = token
    return token

def check_csrf_token():
    csrf_token = request.form.get(_AUTHENTICITY_TOKEN)
    right_csrf_token = session[_CSRF_TOKEN]
    if csrf_token and (csrf_token == right_csrf_token):
        return csrf_token
    else:
        return None

def check_csrf_token_meta_tag():
    csrf_token = request.form.get(_AUTHENTICITY_TOKEN)
    right_csrf_token = session[_CSRF_TOKEN_META_TAG]
    if csrf_token and (csrf_token == right_csrf_token):
        return csrf_token
    else:
        return None

def csrf_token_meta_tag():
    token = secrets.token_urlsafe()
    session[_CSRF_TOKEN_META_TAG] = token
    return token


def template_functions():
    return dict(full_title=full_title, csrf_token_meta_tag=csrf_token_meta_tag)
