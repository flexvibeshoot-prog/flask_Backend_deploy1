from flask import Blueprint,jsonify,request
from flask_jwt_extended import get_jwt_identity,jwt_required
from app.models import Notification
from app import db
# from app import socketio
# from app.tasks.app_notification.firebase_notification import send_firebase_notification

user_notify=Blueprint("user_notify",__name__,url_prefix="/user_notify")

# @user_notify.route("/notify", methods=["POST"])
# # @jwt_required()
# def notify():
#     socketio.emit("notification", {"msg": "Redis test"},room="user_ai24.kanchanbaran.hazra@stcet.ac.in")
#     from app.tasks.app_notification.firebase_notification import send_push_notification
#     send_push_notification.delay(
#         'user_email',
#         "New Notification",
#         'message'
#     )
#     return jsonify({"status": "sent"})


@user_notify.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    user_email = get_jwt_identity()
    from app.tasks.simple_task import get_userID
    user_id=get_userID(user_email)
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([
        {"id": n.id, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat()}
        for n in notifications
    ])



@user_notify.route("/notifications/<int:notif_id>/read", methods=["POST"])
@jwt_required()
def mark_read(notif_id):
    user_id = get_jwt_identity()
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({"status": "marked read"})
    return jsonify({"status": "not found"}), 404
