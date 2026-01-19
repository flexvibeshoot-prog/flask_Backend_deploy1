from app.celery_app import celery

@celery.task(name="app.tasks.log_task.log_task")
def log_task(message):
    print("LOG:", message)


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def deleate_review(self,product_id,user_email):
    from app.models import Review
    from app import db
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)
    review = Review.query.filter_by(
        product_id=product_id,
        user_id=user_id
    ).first()

    if not review:
        return "review not exist"

    db.session.delete(review)
    db.session.commit()
    return "sucess"


@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def set_pin_info(pincode, latitude, longitude, is_serviceable=True):
    from app.models import Pincode
    from app import db

    pin = Pincode.query.filter_by(pincode=pincode).first()
    if not pin:
        pin = Pincode(
            pincode=pincode,
            latitude=latitude,
            longitude=longitude,
            is_serviceable=is_serviceable
        )
        db.session.add(pin)
    else:
        pin.latitude = latitude
        pin.longitude = longitude
        pin.is_serviceable = is_serviceable

    db.session.commit()
    return pin