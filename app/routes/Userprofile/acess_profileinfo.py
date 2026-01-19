from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.models import User
from app import db
from werkzeug.security import check_password_hash,generate_password_hash
import cloudinary.uploader
from datetime import datetime,timedelta

profile=Blueprint('get_profile',__name__,url_prefix='/get_profile')

@profile.route('/get_info',methods=['GET'])
@jwt_required()
def get_profile_info():
    user_identity=get_jwt_identity()
    user=User.query.filter_by(email=user_identity).first()

    if not user:
        return jsonify({'message':'user not found..'})
    
    ##Optiona if frontend not call home rought then it shuld be enable.
    if datetime.utcnow() - user.created_at < timedelta(minutes=5):
        from app.tasks.email_for_user_join import user_welcomeEmail
        user_welcomeEmail.delay(user.email,user.full_name)

    from app.tasks.simple_task.search_relates_simple_task.meilisearch_fun import search_ready
    from app.redis.redis_lock import enqueue_once,indexing_once
    from app.tasks.heavy_task import rebuild_search_index,add_filter_attributes
    if not search_ready():
        res=enqueue_once(rebuild_search_index)
        res1=indexing_once(add_filter_attributes)
        print("Rebuild task enqueued:", res,res1)

    return jsonify({'message':'success',
                    'name':user.full_name,
                    'email':user.email,
                    'avatar_url':user.avatar_url,
                    'phone':user.phone})



@profile.route('/update',methods=['PATCH'])
@jwt_required()
def update_profile_info():
    user_identity=get_jwt_identity()
    user=User.query.filter_by(email=user_identity).first()

    if not user:
        return jsonify({'message':'user not found..'})
    
    data=request.get_json()
    allowed_fields = ['name','phone']

    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Profile updated",
        "updated_fields": list(data.keys())
    }), 200



@profile.route('/change_password',methods=['POST'])
@jwt_required()
def change_password():
    user_identity=get_jwt_identity()
    user=User.query.filter_by(email=user_identity).first()

    if not user:
        return jsonify({'message':'user not found..'})

    data=request.get_json()
    old_password=data.get('old_password')
    new_password=data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message':'old and new passwords are required'}), 400

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'message':'incorrect old password'}), 400

    user.password_hash=generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message':'password changed successfully'}), 200


@profile.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if 'avatar' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['avatar']

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file,
        folder="avatars",
        public_id=f"user_{user_id}",
        overwrite=True
    )

    user.avatar = upload_result['secure_url']
    db.session.commit()

    return jsonify({
        "message": "Avatar updated",
        "avatar_url": user.avatar
    }), 200





