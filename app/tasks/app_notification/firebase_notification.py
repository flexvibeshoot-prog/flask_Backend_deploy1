from app.celery_app import celery
from firebase_admin import messaging

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},queue='email_queue')
def send_push_notification(self,tokens, title, body):
    print(tokens,"notifications tokens found")
    for t in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=t.token
        )

        messaging.send(message)

