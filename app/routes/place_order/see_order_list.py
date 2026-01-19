from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.models import Order


see_orders=Blueprint("see_orders",__name__,url_prefix="order_list")

@see_orders.route('/orderrs')
@jwt_required()
def orders_list():
    email=get_jwt_identity()
    from app.tasks.simple_task import get_userID
    from app.tasks.simple_task.pamentAndOrderrelated_small_fun import get_Address_using_order_id
    user_id=get_userID(email)
    orders=Order.query.filter_by(user_id=user_id).all()

    list_of_order=[]
    for order in orders:
        list_of_order.append({
            "order_id":order.order_id,
            "user_id":order.user_id,
            "address":get_Address_using_order_id(order.order_id),
            "total_amount":order.total_amount,
            "status":order.status,
            "razorpay_order_id":order.razorpay_order_id,
            "created_at":order.created_at
        })
    return jsonify({"orders":list_of_order})





