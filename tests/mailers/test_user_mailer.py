from sampleapp.mailers import user_mailer
from sampleapp.models.user import User
import re
import urllib.parse

def test_account_activation(app, test_users):
    user = test_users['michael']
    with app.test_request_context('/'):
    #with client:
        user.activation_token = User.new_token()
        msg = user_mailer.account_activation(user)
        assert 'Account activation' == msg.subject
        assert [f'{user.email}'] == msg.recipients
        assert 'noreply@example.com' == msg.sender
        assert re.search(user.name, msg.body)
        assert re.search(user.activation_token, msg.body)
        assert re.search(urllib.parse.quote(user.email), msg.body)
