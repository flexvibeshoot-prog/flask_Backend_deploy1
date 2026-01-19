# redis_client.py
import redis
import ssl
import os
# from dotenv import load_dotenv

# load_dotenv()

redis_client = redis.from_url(
    os.getenv('CELERY_BROKER_URL'),
    ssl_cert_reqs=ssl.CERT_NONE,
    decode_responses=True
)
