from flask import Blueprint,jsonify,request,render_template,redirect,url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order,OrderItem,Payment,PaymentMethod,OrderStatusHistory
from app import db
import razorpay
from config import Config
import hmac
import hashlib

order=Blueprint('order',__name__,url_prefix='/order_placed')

@order.route('/create',methods=['POST'])
@jwt_required()
def order_create():
    user_email = get_jwt_identity()
    data = request.get_json()

    from app.tasks.simple_task.amount_calc import calculate_total_ammount
    total_amount=calculate_total_ammount(data['product_id'],data['quantity'])
    if total_amount<0:
        return jsonify({"message":"Inventory is low...!!!"})
    
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)
    if user_id<0:
        return jsonify({"message":"User not exist...!!!"})
    
    new_order=Order(
        user_id=user_id,
        address_id=data['address_id'],
        total_amount=total_amount,
    )

    db.session.add(new_order)
    db.session.flush()  # get order_id

    new_orderItem=OrderItem(
        order_id=new_order.order_id,
        product_id=data['product_id'],
        quantity=data['quantity'],
        price=total_amount
    )
    db.session.add(new_orderItem)

    history = OrderStatusHistory(
        order_id=new_order.order_id,
        status="PLACED",
        message="Order placed successfully"
    )
    db.session.add(history)
    
    try:
        db.session.commit()
        return jsonify({
            "order_id": new_order.order_id,
            "amount": total_amount,
            "status": new_order.status
        })
    except:
        db.session.rollback()
        return jsonify({"message":"Somthing was wrong in data...!!!"})


@order.route('/select_payment',methods=['POST'])
@jwt_required()
def select_payment():
    user_email=get_jwt_identity()
    data=request.get_json()

    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)
    order=Order.query.filter_by(order_id=data['order_id'],user_id=user_id).first()
    if not order:
        return jsonify({"message":"Order not found or unauthorized access...!!!"})

    from app.tasks.simple_task.amount_calc import get_payment_method_id
    method_id=get_payment_method_id(data['method'])

    if method_id<0:
        return jsonify({'message':"No payment method exist...!!!"})
    
    from app.tasks.simple_task.amount_calc import get_order_amount
    amount=get_order_amount(data['order_id'])

    if amount<0:
        return jsonify({"message":"order_id is not exist...!!!"})
    
    new_payment=Payment(
        order_id=data['order_id'],
        method_id=method_id,
        amount=amount
    )
    try:
        db.session.add(new_payment)
        # db.session.flush()  # get payment_id
        db.session.commit()
        if method_id==2:
            from app.tasks.send_emailFor_orderPlaced import order_confirmation_email
            order_confirmation_email.delay(user_email,new_payment.payment_id)
            from app.tasks.simple_task.pamentAndOrderrelated_small_fun import get_product_id_from_order_id
            products_info=get_product_id_from_order_id(data['order_id'])
            from app.tasks.task_after_payment import manage_inventory
            manage_inventory.delay(1,products_info)  #1 for order placed triger
            from app.tasks.simple_task.get_delivery_estimation import get_delivery_date_estimate
            delivary_estimate_date=get_delivery_date_estimate(data['order_id'])
        return jsonify({
            "order_id":data['order_id'],
            "payment_id":new_payment.payment_id,
            "amount":amount,
            "status":new_payment.payment_status,
            "delivary_estimate_date":str(delivary_estimate_date) if method_id==2 else "N/A"
        })
    except:
        db.session.rollback()
        return jsonify({"message":"Failed to create payment...!!!"})


#For online payment inventory management
# @order.route('/after_online_payment',methods=['POST'])
# @jwt_required()
# def after_online_payment():
#     data=request.get_json()
#     from app.tasks.simple_task.pamentAndOrderrelated_small_fun import get_product_id_from_order_id
#     products_info=get_product_id_from_order_id(data['order_id'])
#     from app.tasks.task_after_payment import manage_inventory
#     manage_inventory.delay(1,products_info)  #1 for order placed triger
#     return jsonify({"message":"Added into queue...!!!"})




@order.route('/set_payment_method',methods=['POST'])
def set_payment_method():
    data=request.get_json()
    new_pament_method=PaymentMethod(name=data['method'])
    db.session.add(new_pament_method)
    try:
        db.session.commit()
        return jsonify({"message":"Added sucessfilly...!!!"})
    except:
        db.session.rollback()
        return jsonify({"message":"Somthing is wrong in data...!!!"})
    


#test the celery task
@order.route('/send_celery')
def send_celery():
    from app.tasks.send_emailFor_orderPlaced import order_confirmation_email
    order_confirmation_email.delay("khazra800@gmail.com")
    return jsonify({"message":"Added to the queue...!!!"})





