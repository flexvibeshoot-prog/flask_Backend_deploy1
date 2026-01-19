from app.models import Admin,User
from flask import Blueprint,request,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt_identity,create_access_token
from werkzeug.security import generate_password_hash,check_password_hash
from app.routes.Otp_genrate import genrate_otp
from datetime import datetime,timedelta
from app import db


admin_acess=Blueprint('admin_acess',__name__,url_prefix='/admin_acess')

@admin_acess('/create-account',methods=['POST'])
def create_AdminAccount():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=data['email']).first()
    admin=Admin.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'message':'Email already in customer List.'})
    if admin:
        return jsonify({'message':'Admin already exist.'})
    
    otp = genrate_otp()
    from app.tasks.Registermessaging_task import send_Adminmail_task
    send_Adminmail_task.delay(
        data['email'],otp,
    )
    
    try:
        admin=Admin(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            otp=otp,
            otp_expiry=datetime.utcnow() + timedelta(minutes=5)
        )
        db.session.add(admin)
        db.session.commit()
        return jsonify({'message':'Admin registered.'})
    except:
        return jsonify({'message':'Somthing wrong in data.'})
    


# 🔐 SIGNIN
@admin_acess.route('/admin_Signin', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    admin = Admin.query.filter_by(email=email).first()

    if not admin:
        return {"msg": "Invalid credentials"}, 401

    # 🔒 Check account lock
    if admin.locked_until and admin.locked_until > datetime.utcnow():
        return {"msg": "Account locked. Try later."}, 403

    if not check_password_hash(admin.password_hash, password):
        admin.failed_attempts += 1

        if admin.failed_attempts >= 5:
            admin.locked_until = datetime.utcnow() + timedelta(minutes=15)

        db.session.commit()
        return {"msg": "Invalid credentials"}, 401

    # ✅ Success
    admin.failed_attempts = 0
    admin.locked_until = None
    admin.last_login_at = datetime.utcnow()
    db.session.commit()

    token = create_access_token(
        identity=admin.email,
        additional_claims={"role": "admin"}
    )

    # resp = jsonify({"msg": "Login success"})
    # set_access_cookies(resp, token)
    # return resp
    return jsonify({"message": "Login successful", "token": token}), 200