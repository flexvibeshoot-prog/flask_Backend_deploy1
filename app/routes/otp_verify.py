from flask import Blueprint,request
from app.models import User
from app import db
from datetime import datetime

otp_ver=Blueprint('otp_ver',__name__,url_prefix='/verify')


@otp_ver.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    email = data.get("email")
    entered_otp = data.get("otp")

    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "User not found"}, 404
    
    # Check expiry
    if user.otp_expiry < datetime.utcnow():
        return {"error": "OTP expired"}, 400
    
    # Check OTP
    if user.otp != entered_otp:
        return {"error": "Invalid OTP"}, 400

    # Success
    user.verified = True
    user.otp = None
    user.otp_expiry = None
    db.session.commit()

    return {"message": "OTP Verified Successfully"}, 200
