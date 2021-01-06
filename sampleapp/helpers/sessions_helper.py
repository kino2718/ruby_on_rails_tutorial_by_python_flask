from flask import g, session, current_app, request, redirect
from ..models.user import User
from datetime import datetime, timedelta
from itsdangerous import URLSafeSerializer

def log_in(user):
    session['id'] = user.id

def forget(user, response):
    user.forget()
    response.delete_cookie(key='user_id')
    response.delete_cookie(key='remember_token')

def log_out(response):
    forget(current_user(), response)
    session.pop('id', None)
    if getattr(g, 'current_user', None):
        del g.current_user

def remember(user, response):
    user.remember()
    # user idに署名する
    # 一見payloadが暗号化されているように見えるが実際にはbase64 encodeされているだけ
    key = current_app.secret_key
    s = URLSafeSerializer(key, salt='remember_me')
    signed_id = s.dumps(user.id)

    # 署名付きuser idとremember_tokenのクッキーを設定
    # 期間無制限（実際にはおおよそ20年後に期限切れ）
    expires = datetime.utcnow() + timedelta(days=365*20)
    response.set_cookie(key='user_id', value=signed_id,
                        expires=expires)
    response.set_cookie(key='remember_token', value=user.remember_token,
                        expires=expires)

def current_user():
    user_id = session.get('id')
    if user_id:
        # g is unique object for each request
        current_user = getattr(g, 'current_user', None)
        if not current_user:
            current_user = User.find(user_id)
            if current_user:
                g.current_user = current_user
        return current_user
    else:
        # cookieからuser id取得を試みる
        signed_id = request.cookies.get('user_id')
        if signed_id:
            try:
                # 署名を確認する
                key = current_app.secret_key
                s = URLSafeSerializer(key, salt='remember_me')
                user_id = s.loads(signed_id)
                user = User.find(user_id)

                # 記憶トークンの確認
                if user and \
                   (remember_token := request.cookies.get('remember_token')) and \
                   (user.authenticated_by_remember_token(remember_token)):
                    log_in(user)
                    g.current_user = user
                    return user
            except BadSignature:
                # 改ざんされている
                return None

        return None

# 渡されたユーザーがカレントユーザーであればtrueを返す
def is_current_user(user):
    if user and user == current_user():
        return True
    else:
        return False

def logged_in():
    if current_user():
        return True
    else:
        return False

# 記憶したURL（もしくはデフォルト値）にリダイレクト
def redirect_back_or(default):
    url = session.get('forwarding_url') or default
    session.pop('forwarding_url', None)
    return redirect(url)

# アクセスしようとしたURLを覚えておく
def store_location():
    if request.method.lower() == 'get':
        session['forwarding_url'] = request.url

def template_functions():
    return dict(current_user=current_user, logged_in=logged_in)
