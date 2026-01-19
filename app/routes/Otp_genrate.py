from flask import Blueprint, jsonify, render_template
from app.btask import task_give_to_thread
import random

email_send = Blueprint("email_send", __name__,url_prefix='/email_send')

#Expired deleat in production
def send_mail(otp,name,email):
    template=render_template('email_config.html',otp=otp,name=name)
    try:
        task_give_to_thread(
            subject="Register to Flex and vibe",
            recipients=[email],
            body="This is register otp, don't share to other person",
            html=template
        )

        return 1
    except:
        return 0


def genrate_otp():
    otp = random.randint(1000, 9999)
    return otp
