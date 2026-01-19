from flask import Blueprint, redirect, request, session, current_app, jsonify
from requests_oauthlib import OAuth2Session
from app.models import User
from app import db
import os
from flask_jwt_extended import create_access_token, create_refresh_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/google/login")
def google_login():
    google = OAuth2Session(
        current_app.config["GOOGLE_CLIENT_ID"],
        scope=current_app.config["SCOPE"],
        redirect_uri=current_app.config["OAUTH_REDIRECT_URI"]
    )

    auth_url, state = google.authorization_url(
        current_app.config["GOOGLE_AUTH_URL"],
        access_type="offline",
        prompt="consent"
    )

    session["oauth_state"] = state
    return redirect(auth_url)


@auth_bp.route("/google/callback")
def google_callback():
    google = OAuth2Session(
        current_app.config["GOOGLE_CLIENT_ID"],
        state=session["oauth_state"],
        redirect_uri=current_app.config["OAUTH_REDIRECT_URI"]
    )

    token = google.fetch_token(
        current_app.config["GOOGLE_TOKEN_URL"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        authorization_response=request.url
    )

    userinfo = google.get(
        current_app.config["GOOGLE_USERINFO_URL"]
    ).json()

    # return jsonify(userinfo)
    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("name")
    avatar = userinfo.get("picture")

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            email=email,
            full_name=name,
            oauth_provider="google",
            oauth_provider_id=google_id,
            avatar_url=avatar,
            verified=True
        )
        db.session.add(user)
    else:
        user.oauth_provider = "google"
        user.oauth_provider_id = google_id

    db.session.commit()
    token = create_access_token(identity=str(user.email))
    ref_token = create_refresh_token(identity=str(user.email))

    return jsonify({
        "message": "OAuth login success",
        "email": user.email,
        "token": token,
        "refresh_token": ref_token
    })
