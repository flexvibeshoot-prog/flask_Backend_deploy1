from celery import Celery
from kombu import Queue
from app import create_app
from config import Config
import ssl

flask_app = create_app()

celery = Celery(
    "worker",
    include=[
        "app.tasks.Registermessaging_task",
        "app.tasks.heavy_task",
        "app.tasks.send_emailFor_orderPlaced",
        "app.tasks.task_after_payment",
        "app.tasks.app_notification.firebase_notification",
        "app.tasks.email_for_user_join"
    ]
)
celery.config_from_object(Config)
# celery.conf.update(flask_app.config)
celery.conf.update(
    broker_url='rediss://default:AaaMAAIncDFkN2E5YWVjM2YzNDA0MzY0YTM0MGM1MDljYzZjY2QwZnAxNDI2MzY@correct-mustang-42636.upstash.io:6379',
    result_backend='rediss://default:AaaMAAIncDFkN2E5YWVjM2YzNDA0MzY0YTM0MGM1MDljYzZjY2QwZnAxNDI2MzY@correct-mustang-42636.upstash.io:6379',

    broker_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE
    },

    task_acks_late=True,
    worker_prefetch_multiplier=1
)

# 🔥 DEFINE QUEUES
celery.conf.task_queues = (
    Queue("default"),
    Queue("email_queue"),
    Queue("heavy_queue"),
)

# 🔥 DEFAULT QUEUE
celery.conf.task_default_queue = "default"

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask