from app.celery_app import celery
from flask_mail import Message
from flask import render_template
from datetime import datetime
from app.models import Payment
from app import mail


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="email_queue")
def order_confirmation_email(self, email, payment_id):
    from app.tasks.simple_task.get_userName import get_userName
    from app.tasks.simple_task.pamentAndOrderrelated_small_fun import (
        get_items_from_order_id,
        get_Address_using_order_id
    )

    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        raise ValueError("Invalid payment_id")

    address = get_Address_using_order_id(payment.order_id)

    html = render_template(
        "order_confirmation.html",
        customer_name=get_userName(email),
        order_id=payment.order_id,
        order_date=payment.created_at,
        payment_status=payment.payment_status,
        total_amount=payment.amount,
        items=get_items_from_order_id(payment.order_id),
        shipping_address=f"{address.get('city')}, {address.get('state')}, {address.get('country')}",
        order_tracking_url=f"https://yourapp.com/orders/{payment.order_id}",
        company_name="Flex and Vibe",
        year=datetime.now().year
    )

    msg = Message(
        subject="Order Confirmed",
        recipients=[email],
        html=html
    )

    mail.send(msg)
    print("Email sent successfully ✅")
