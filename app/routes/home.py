from flask import Blueprint,jsonify,request
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from datetime import datetime,timedelta

home = Blueprint('home', __name__, url_prefix='/home')


# 🛡️ PROTECTED ROUTE
@home.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()  # email from token
    user = User.query.filter_by(email=current_user).first()

    # Welcome email
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

    return jsonify({
        "full_name": user.full_name,
        "email": user.email
    })