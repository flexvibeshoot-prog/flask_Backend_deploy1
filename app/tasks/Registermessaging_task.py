from app.celery_app import celery
from app import mail
from flask_mail import Message
from flask import render_template

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="email_queue")
def send_mail_task(self, email, otp, name):
    template = render_template(
        "registration_email.html",
        otp=otp,
        name=name
    )

    msg = Message(
        subject="Register to Flex and vibe",
        recipients=[email],
        # body="This is register otp, don't share to other person.\n OTP is valid for 5 minutes.",
        html=template
    )
    mail.send(msg)


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="email_queue")
def send_Forget_mail_task(self, email, otp):
    template = render_template(
        "forgate_pass_otp.html",
        otp=otp
    )

    msg = Message(
        subject="Register to Flex and vibe",
        recipients=[email],
        body="This is register otp, don't share to other person.\n OTP is valid for 5 minutes.",
        html=template
    )
    mail.send(msg)


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="email_queue")
def send_Adminmail_task(self, email, otp):

    msg = Message(
        subject="Register to Flex and vibe",
        recipients=[email],
        body=f"This is register otp{otp}, don't share to other person.\n OTP is valid for 5 minutes.",
    )
    mail.send(msg)