from app.celery_app import celery
from app import db
from app.models import Order, OrderStatusHistory

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def update_order_status(order_id, status, message):
    order = Order.query.get(order_id)
    order.status = status

    history = OrderStatusHistory(
        order_id=order_id,
        status=status,
        message=message
    )

    db.session.add(history)
    db.session.commit()
