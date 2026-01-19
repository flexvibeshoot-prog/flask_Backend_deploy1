from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.redis.redis_setup import redis_client as redis
from config import Config


userLogout=Blueprint('userLogout', __name__, url_prefix='/userLogout')


@userLogout.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis.set(jti, "revoked", ex=Config.JWT_ACCESS_TOKEN_EXPIRES)
    return jsonify({"msg": "Logged out"})

@userLogout.route("/logout_refresh", methods=["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    refresh_jti = get_jwt()["jti"]
    redis.set(refresh_jti, "revoked", ex=Config.JWT_REFRESH_TOKEN_EXPIRES)
    return jsonify({"msg": "Logged out fully"})

