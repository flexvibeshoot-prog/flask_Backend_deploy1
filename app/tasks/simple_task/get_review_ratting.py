from app import db
from app.models import Review

from sqlalchemy import func
def product_rating(product_id):
    avg = db.session.query(func.avg(Review.rating))\
        .filter_by(product_id=product_id)\
        .scalar()
    return avg