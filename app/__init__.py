from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask_jwt_extended import JWTManager,verify_jwt_in_request,get_jwt_identity
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate 
from flask_apscheduler import APScheduler
from datetime import datetime,timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO,join_room,disconnect,emit
import firebase_admin
from firebase_admin import credentials
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

db = SQLAlchemy()
jwt = JWTManager()
mail=Mail()
migrate=Migrate()
# Schudule=BackgroundScheduler()

# function for rate-limiter 
# def user_rate_limit():
#     verify_jwt_in_request(optional=True)
#     user_id = get_jwt_identity()
#     return str(user_id) if user_id else get_remote_address()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]   # 🔥 GLOBAL DEFAULT LIMIT
)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)

    # Redis-backed limiter
    limiter.storage_uri = app.config["RATELIMIT_STORAGE_URI"]
    limiter.init_app(app)

    # for logout
    from app.redis.redis_setup import redis_client as redis
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return redis.exists(jwt_payload["jti"])
    
    mail.init_app(app)
    migrate.init_app(app,db)
    Schudule=BackgroundScheduler()
    Schudule.start()
    CORS(app,supports_credentials=True,origins='*')
    

    # 🔥 Firebase initialization (only once)
    if not firebase_admin._apps:
        cred = credentials.Certificate(app.config["FIREBASE_CREDENTIALS"])
        firebase_admin.initialize_app(cred)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.userLogin import login
    app.register_blueprint(login)
    
    from app.routes.home import home
    app.register_blueprint(home)

    from app.routes.product import product
    app.register_blueprint(product)

    from app.routes.Otp_genrate import email_send
    app.register_blueprint(email_send)

    from app.routes.otp_verify import otp_ver
    app.register_blueprint(otp_ver)
    
    from app.routes.Oauth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.Userprofile.acess_profileinfo import profile
    app.register_blueprint(profile)

    from app.routes.set_address import address
    app.register_blueprint(address)

    from app.routes.place_order.razorpay import razor_api
    app.register_blueprint(razor_api)

    from app.routes.place_order.order_placed import order
    app.register_blueprint(order)

    from app.routes.cart_wishlist.cart_wirhlist import cart
    app.register_blueprint(cart)

    from app.routes.cart_wishlist.get_cart_item import get_cart_item
    app.register_blueprint(get_cart_item)

    from app.routes.search_roughts.product_search import search
    app.register_blueprint(search)

    from app.routes.review_rating.review import review_bp
    app.register_blueprint(review_bp)

    from app.routes.userLogout import userLogout
    app.register_blueprint(userLogout)

    from app.routes.permison_user.allow_notify import allow_notify
    app.register_blueprint(allow_notify)

    from app.routes.notification.user_notification import user_notify
    app.register_blueprint(user_notify)
    
    # ✅ Cloudinary Config
    cloudinary.config(
        cloud_name = app.config['CLOUDINARY_CLOUD_NAME'],
        api_key = app.config['CLOUDINARY_API_KEY'],
        api_secret = app.config['CLOUDINARY_API_SECRET']
    )
    
    from app.btask import delete_unverified_users
    # Run the job every 24 hours
    Schudule.add_job(
        func=delete_unverified_users,
        trigger=IntervalTrigger(hours=24),
        args=[app],
        id="cleanup_unverified_users",
        replace_existing=True
    )

    # 🔥 Custom 429 error handler
    @app.errorhandler(429)
    def ratelimit_error(e):
        return render_template(
            "errors/429.html",
            retry_after=e.retry_after
        ), 429

    # ✅ Create tables within app context
    with app.app_context():
        db.create_all()

    return app
