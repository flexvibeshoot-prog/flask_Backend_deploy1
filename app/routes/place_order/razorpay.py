from flask import Blueprint,request,jsonify
import razorpay
import hmac
import hashlib
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order

razor_api=Blueprint("razor_api",__name__,url_prefix='/razorpay')


def get_razorpay_client():
    return razorpay.Client(
        auth=(
            Config.RAZORPAY_KEY_ID,
            Config.RAZORPAY_KEY_SECRET
        )
    )

# ============================
# Create Razorpay Order
# ============================
@razor_api.route("/create-order", methods=["POST"])
@jwt_required()
def create_order():
    email=get_jwt_identity()
    data = request.get_json()
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(email)
    user_order = Order.query.filter_by(order_id=data['order_id'], user_id=user_id).first()
    if not user_order:
        return jsonify({"message":"Order not found or unauthorized access...!!!"})
    # from app.tasks.amount_calc import calculate_total_ammount
    # amount=calculate_total_ammount(data['order_id'])
    # if amount<0:
    #     return jsonify({"message":"Wrong order id...!!!"})
    amount = data['amount'] * 100  # rupees → paise

    client = get_razorpay_client()

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    user_order.razorpay_order_id = order["id"]
    from app import db
    db.session.commit()

    return jsonify({
        "order_id": order["id"],
        "key": Config.RAZORPAY_KEY_ID,
        "amount": amount,
        "currency": "INR"
    })


# ============================
# Verify Payment
# ============================
@razor_api.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json

    razorpay_order_id = data["razorpay_order_id"]
    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_signature = data["razorpay_signature"]

    body = razorpay_order_id + "|" + razorpay_payment_id

    expected_signature = hmac.new(
        bytes(Config.RAZORPAY_KEY_SECRET, 'utf-8'),
        bytes(body, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    if expected_signature == razorpay_signature:

        #inventory management task
        from app.tasks.simple_task.pamentAndOrderrelated_small_fun import order_id_from_razorpay_order_id
        order_id = order_id_from_razorpay_order_id(razorpay_order_id,razorpay_payment_id)
        from app.tasks.simple_task.pamentAndOrderrelated_small_fun import get_product_id_from_order_id
        products_info=get_product_id_from_order_id(order_id)
        from app.tasks.task_after_payment import manage_inventory
        manage_inventory.delay(1,products_info)

        #estimade delivary date
        from app.tasks.simple_task.get_delivery_estimation import get_delivery_date_estimate
        delivary_estimate_date=get_delivery_date_estimate(data['order_id'])

        #email task
        from app.tasks.simple_task.pamentAndOrderrelated_small_fun import get_email_from_razorpay_payment_id
        user_email=get_email_from_razorpay_payment_id(razorpay_payment_id)
        from app.models import Payment
        payment=Payment.query.filter_by(razorpay_payment_id=razorpay_payment_id).first()
        payment_id=payment.payment_id
        from app.tasks.send_emailFor_orderPlaced import order_confirmation_email
        order_confirmation_email.delay(user_email,payment_id)
        return jsonify({"status": "success","delivary_estimate_date":str(delivary_estimate_date)})
    else:
        return jsonify({"status": "failed"}), 400