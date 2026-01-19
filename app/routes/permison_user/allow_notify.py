from flask import Blueprint,request
from app import db
from app.models import PushToken
from flask_jwt_extended import jwt_required,get_jwt_identity

allow_notify=Blueprint('allow_notify',__name__,url_prefix='/allow')

@allow_notify.route("/save_push_token", methods=["POST"])
@jwt_required()
def save_token():
    user_email = get_jwt_identity()
    data = request.get_json()
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)

    PushToken.query.filter_by(
        user_id=user_id,
        token=data["fcm_token"]
    ).delete()

    push = PushToken(
        user_id=user_id,
        token=data["fcm_token"],
        device_type=data.get("device_type", "unknown")
    )

    db.session.add(push)
    db.session.commit()

    return {"status": "saved"}
