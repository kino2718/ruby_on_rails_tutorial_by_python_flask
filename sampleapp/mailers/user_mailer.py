from flask import render_template
from flask_mail import Message

def account_activation(user):
    msg = Message(
        subject='Account activation',
        sender='noreply@example.com',
        recipients=[user.email])
    msg.body = render_template('user_mailer/account_activation.text', user=user)
    msg.html = render_template('user_mailer/account_activation.html', user=user)
    return msg
