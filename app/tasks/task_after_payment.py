from app.celery_app import celery
from app import mail
from flask_mail import Message
from flask import render_template
from app.models import Inventory
from app import db

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def manage_inventory(self, status,products_info):
    if status==0: #order canciled
        for product_info in products_info:
            inventory=Inventory.query.filter_by(product_id=product_info['product_id']).first()
            inventory.quantity=inventory.quantity+product_info['quantity']
        db.session.commit()
        print('sucess...!!!')
    elif status==1: #order placed
        for product_info in products_info:
            inventory=Inventory.query.filter_by(product_id=product_info['product_id']).first()
            inventory.quantity=inventory.quantity-product_info['quantity']
        db.session.commit()
        print('sucess...!!!')
    else:
        return "Failed inventory process due to status code...!!!"