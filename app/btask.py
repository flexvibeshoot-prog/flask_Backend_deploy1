from flask_mail import Message
from app import mail
from threading import Thread
from flask import current_app
from datetime import datetime,timedelta
from app.models import User
from app import db

# old email setup
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def task_give_to_thread(subject, recipients, body, html=None):
    app=current_app._get_current_object()

    msg = Message(subject=subject, recipients=recipients)
    msg.body = body

    if html:
        msg.html = html

    thread = Thread(target=send_async_email, args=(app, msg))
    thread.start()
    return thread

# run every 24 hour
def delete_unverified_users(app):

    expiry_time = datetime.utcnow() - timedelta(hours=24)

    with app.app_context():
        unverified_users = User.query.filter(
            User.verified == False,
            User.created_at < expiry_time
        ).all()

        for user in unverified_users:
            db.session.delete(user)

        db.session.commit()
    print("Cleaned unverified accounts")