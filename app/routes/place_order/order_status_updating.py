from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, OrderItem, Payment, PaymentMethod, OrderStatusHistory
from app.tasks.order_update_task import update_order_status


status_update = Blueprint('order_status_update', __name__, url_prefix='/order_status_update')


@status_update.route('/update_packed', methods=['POST'])
@jwt_required()
def update_order_packed():
    user_email = get_jwt_identity()
    data = request.get_json()
    order = Order.query.filter_by(order_id=data['order_id']).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    update_order_status.delay(data['order_id'], "PACKED", "Items packed in warehouse")
    return jsonify({"message": "Order status updated to PACKED"})

@status_update.route('/update_shipped', methods=['POST'])
@jwt_required()
def update_order_shipped():
    user_email = get_jwt_identity()
    data = request.get_json()
    order = Order.query.filter_by(order_id=data['order_id']).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    update_order_status.delay(data['order_id'], "SHIPPED", "Shipped via BlueDart")
    return jsonify({"message": "Order status updated to SHIPPED"})

@status_update.route('/update_outfor_delivery', methods=['POST'])
@jwt_required()
def update_outfor_delivery():
    user_email = get_jwt_identity()
    data = request.get_json()
    order = Order.query.filter_by(order_id=data['order_id']).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    update_order_status.delay(data['order_id'], "Out for Delivery", "Order delivered to customer")
    return jsonify({"message": "Order status updated to Out for Delivery"})

@status_update.route('/update_delivered', methods=['POST'])
@jwt_required()
def update_order_delivered():
    user_email = get_jwt_identity()
    data = request.get_json()
    order = Order.query.filter_by(order_id=data['order_id']).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    update_order_status.delay(data['order_id'], "DELIVERED", "Order delivered to customer")
    return jsonify({"message": "Order status updated to DELIVERED"})