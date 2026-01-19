from flask import Blueprint, jsonify
from app.models import Order, OrderStatusHistory
from flask_jwt_extended import jwt_required, get_jwt_identity

order_track_bp = Blueprint("order_track", __name__, url_prefix="/order_track")


@order_track_bp.route("/track/<order_number>")
@jwt_required()
def track_order(order_number):
    order = Order.query.filter_by(order_id=order_number).first_or_404()

    history = OrderStatusHistory.query.filter_by(
        order_id=order.order_id
    ).order_by(OrderStatusHistory.created_at.asc())

    return jsonify({
        "order_number": order.order_id,
        "current_status": order.status,
        "timeline": [
            {
                "status": h.status,
                "message": h.message,
                "time": h.created_at
            } for h in history
        ]
    })
