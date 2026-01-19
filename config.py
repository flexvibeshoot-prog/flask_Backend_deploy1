import os
from time import time
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')

    # MASTER (write) Automatically handeled by TiDB Cloud
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://47vaDr39q2MWZRN.root:"
        "xypzX71xUJG00aro"
        "@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/"
        "test"
        "?ssl_verify_cert=true"
        "&ssl_verify_identity=true"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS=False

    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION=["headers"]
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30)

    # ---------- CLOUDINARY ----------
    CLOUDINARY_CLOUD_NAME =os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

    # ---------- FLASK MAIL ----------
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # ---------- GOOGLE OAUTH ----------
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET =os.getenv('GOOGLE_CLIENT_SECRET')

    GOOGLE_AUTH_URL = os.getenv('GOOGLE_AUTH_URL')
    GOOGLE_TOKEN_URL = os.getenv('GOOGLE_TOKEN_URL')
    GOOGLE_USERINFO_URL = os.getenv('GOOGLE_USERINFO_URL')

    # MUST match Google Console redirect URI
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI')

    # OAuth scope used in your route
    SCOPE = [
        "openid",
        "email",
        "profile"
    ]

    # CELERY_BROKER_URL="redis://localhost:6379/0"
    # CELERY_RESULT_BACKEND="redis://localhost:6379/0"

    RAZORPAY_KEY_ID=os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET=os.getenv('RAZORPAY_KEY_SECRET')

    #celery configuration
    broker_url = os.getenv('CELERY_BROKER_URL')
    result_backend = os.getenv('CELERY_RESULT_BACKEND')
    RATELIMIT_STORAGE_URI = broker_url
    SOCKETIO_MESSAGE_QUEUE=broker_url

    task_default_queue = "default"

    task_queues = {
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "email_queue": {
            "exchange": "email",
            "routing_key": "email.send",
        },
        "heavy_queue": {
            "exchange": "heavy",
            "routing_key": "heavy.process",
        },
    }

    task_routes = {
        "app.tasks.send_mail.send_mail_task": {"queue": "email_queue"},
        "app.tasks.heavy.*": {"queue": "heavy_queue"},
    }

    # redis indexin to prevent duplicatte
    LOCK_KEY = os.getenv('LOCK_KEY')
    LOCK_KEY_INDEXING= os.getenv('LOCK_KEY_INDEXING')

    GEOLOCATION_URL=os.getenv('GEOLOCATION_URL')
    GEOLOCATION_API_KEY=os.getenv('GEOLOCATION_API_KEY')

    ADMIN_LAT=os.getenv('ADMIN_LAT')
    ADMIN_LONG=os.getenv('ADMIN_LONG')

    # Firebase
    FIREBASE_CREDENTIALS = os.path.join(
        os.path.dirname(__file__),
        "firebase_service_account.json"
    )
