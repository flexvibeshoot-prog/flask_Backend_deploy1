from app.celery_app import celery
from flask import render_template
from flask_mail import Message
from app import mail
from datetime import datetime


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="email_queue")
def user_welcomeEmail(self, email, name):
    template = render_template(
        "user_WelcomeEmail.html",
        UserName=name,
        Year=datetime.now().year
    )

    msg = Message(
        subject="Welcome",
        recipients=[email],
        html=template
    )
    mail.send(msg)