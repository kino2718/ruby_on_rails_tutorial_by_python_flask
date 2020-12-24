from flask import session, request
import secrets

_CSRF_TOKEN = 'csrf_token'

def csrf_token():
    token = secrets.token_hex()
    session[_CSRF_TOKEN] = token
    return token

def check_csrf_token():
    csrf_token = request.form.get('authenticity_token')
    right_csrf_token = session[_CSRF_TOKEN]
    if right_csrf_token:
        del session[_CSRF_TOKEN]
    if csrf_token and (csrf_token == right_csrf_token):
        return csrf_token
    else:
        return None

def template_functions():
    def full_title(page_title = ''):
        base_title = 'Ruby on Rails Tutorial Sample App'
        if not page_title:
            return base_title
        else:
            return f'{page_title} | {base_title}'

    return dict(full_title=full_title)
