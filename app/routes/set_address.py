from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.models import Address,Notification,PushToken
from app import db
# from app.tasks.app_notification.firebase_notification import send_push_notification

address=Blueprint('address',__name__,url_prefix='/set_address')

@address.route('/address_set',methods=['POST'])
@jwt_required()
def set_address():
    user_email=get_jwt_identity()
    data=request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    required_fields = [
        "phone", "address_line1", "city",
        "state", "country", "pin_code"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    #background task.
    from app.tasks.simple_task.get_userID import get_userid
    from app.tasks.simple_task.get_userName import get_userName
    user_id=get_userid(user_email)
    new_address=Address(
        user_id=user_id,
        full_name=get_userName(user_email),
        phone=data['phone'],
        address_line1=data['address_line1'],
        address_line2=data['address_line2'],
        city=data['city'],
        state=data['state'],
        country=data['country'],
        postal_code=data['pin_code']
    )
    message="New address added in tour account."
    # Save notification in DB
    notif = Notification(user_id=user_id, releted_link='/set_address/get_address', message=message)
    try:
        db.session.add(notif)
        db.session.add(new_address)
        db.session.commit()
        from app.routes.notification.pubish_notification import send
        send(user_email,message)
        # tokens = PushToken.query.filter_by(user_id=user_id).all()
        # from app.tasks.app_notification.firebase_notification import send_push_notification
        # send_push_notification.delay(tokens, "Address Added", message)
        return jsonify({"message":"Address is added sucessfully...!!!"})
    except:
        db.session.rollback()
        return jsonify({"message":"Somthing is wrong in data...!!!"})
    



@address.route('/get_address',methods=['GET'])
@jwt_required()
def get_address():
    user_email=get_jwt_identity()
    #background task.
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)
    addresses=Address.query.filter_by(user_id=user_id).all()
    address_list=[]
    for addr in addresses:
        address_data={
            "id":addr.user_id,
            "full_name":addr.full_name,
            "phone":addr.phone,
            "address_line1":addr.address_line1,
            "address_line2":addr.address_line2,
            "city":addr.city,
            "state":addr.state,
            "country":addr.country,
            "pin_code":addr.postal_code,
            "is_default":addr.is_default
        }
        address_list.append(address_data)
    return jsonify({"addresses":address_list})