from flask import Blueprint, app,jsonify,request
from app import db
from app.models import Role, User
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token,jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from app.routes.Otp_genrate import genrate_otp

DEFAULT_AVATER="./static/avaterS/default_avater.png"


login=Blueprint('userLogin', __name__, url_prefix='/userLogin')


@login.route('/add_role', methods=['POST'])
def add_role():
    data = request.get_json()

    # 1️⃣ Validate input
    if not data or 'role_name' not in data:
        return jsonify({"error": "role_name is required"}), 400

    try:
        # 2️⃣ Create and add new role
        new_role = Role(role_name=data['role_name'])
        db.session.add(new_role)
        db.session.commit()
        return jsonify({"message": "Role added successfully"}), 201

    except IntegrityError:
        # 3️⃣ Handle unique constraint violation
        db.session.rollback()
        return jsonify({"error": "Role already exists"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
# 📝 SIGNUP
@login.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data.get("email") or not data.get("password") or not data.get("full_name"):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=data['email']).first()

    # CASE 1: User already exists
    if user:
        # OAuth user exists but no password yet
        if user.password_hash is None:
            hashed_pw = generate_password_hash(data['password'])
            user.password_hash = hashed_pw
            user.full_name = data['full_name']
            user.auth_provider = 'local'

            db.session.commit()

            return jsonify({
                "message": "Password added to existing Google account"
            }), 200

        # Email+password already exists
        return jsonify({"error": "Email already registered"}), 400

    # CASE 2: New user (normal signup)
    otp = genrate_otp()
    from app.tasks.Registermessaging_task import send_mail_task
    send_mail_task.delay(
        data['email'],otp, data['full_name'], 
    )

    hashed_pw = generate_password_hash(data['password'])

    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        password_hash=hashed_pw,
        avatar_url=DEFAULT_AVATER,
        oauth_provider='local'
    )

    new_user.otp = str(otp)
    new_user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

    
# 🔐 SIGNIN
@login.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']) or not user.verified:
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token (valid for 1 hour)
    token = create_access_token(identity=str(user.email))
    ref_token = create_refresh_token(identity=str(user.email))
    return jsonify({"message": "Login successful", "token": token, "refresh_token": ref_token})


# 🔄 REFRESH TOKEN
@login.route('/kbrefresh_token', methods=['POST'])
@jwt_required(refresh=True)
def kbrefresh_token():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({"token": new_token}), 200

#Resend OTP
@login.route('/resend_otp',methods=['POST'])
def resend_otp():
    data = request.get_json()
    try:
        new_user=User.query.filter_by(email=data['email']).first()
        if not new_user:
            return jsonify({'message':"User not found.!!"}), 400
    except:
        return jsonify({'message':"User not found.!!"}), 400

    otp=genrate_otp()
    from app.tasks.Registermessaging_task import send_mail_task
    send_mail_task.delay(
        data['email'],otp, new_user.full_name, 
    )

    new_user.otp = str(otp)
    new_user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    return jsonify({"message": "OTP sended",'sig':1}), 201
    

# forgate password
@login.route('/forgate_password',methods=['POST'])
def forgate_password():
    data = request.get_json()
    try:
        new_user=User.query.filter_by(email=data['email']).first()
    except:
        return jsonify({'message':"User not found.!!"}), 400
    
    password1=data['password1']
    password2=data['password2']

    if password1!=password2:
        return jsonify({'message':'Check conform password.'})
    
    new_user.password_hash=generate_password_hash(password1)
    db.session.commit()

    return jsonify({'message':"sucess message.."})


@login.route('/send_forgate_email',methods=['POST'])
def forgate_email():
    data = request.get_json()
    new_user=User.query.filter_by(email=data['email']).first()
    if not new_user:
        return jsonify({"message":"User not found.."})
    
    otp=genrate_otp()
    from app.tasks.Registermessaging_task import send_Forget_mail_task
    send_Forget_mail_task.delay(data['email'],otp)

    new_user.otp = str(otp)
    new_user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    return jsonify({"message": "OTP sended",'sig':1}), 201











