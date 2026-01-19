from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Review, ReviewImage
from datetime import datetime
from sqlalchemy import func

review_bp = Blueprint("review", __name__, url_prefix="/reviews")


@review_bp.route("/add_review", methods=["POST"])
@jwt_required()
def add_review():
    user_email = get_jwt_identity()
    data = request.get_json()
    from app.tasks.simple_task.get_userID import get_userid
    user_id=get_userid(user_email)

    product_id = data.get("product_id")
    rating = data.get("rating")
    comment = data.get("comment", "")
    # images = data.get("images", [])

    if not product_id or not rating:
        return jsonify({"message": "product_id and rating required"}), 400

    # prevent duplicate review
    existing = Review.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()

    if existing:
        return jsonify({"message": "You already reviewed this product"}), 400

    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        created_at=datetime.utcnow()
    )

    db.session.add(review)
    # db.session.flush()  # get review_id before commit

    # for img_url in images:
    #     img = ReviewImage(
    #         review_id=review.review_id,
    #         image_url=img_url
    #     )
    #     db.session.add(img)

    db.session.commit()

    return jsonify({"message": "Review added successfully"}), 201


@review_bp.route("/product/<int:product_id>", methods=["GET"])
def get_product_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).order_by(
        Review.created_at.desc()
    ).all()
    from app.tasks.simple_task.get_userID import get_mailFromID

    result = []

    for r in reviews:
        result.append({
            "review_id": r.review_id,
            "user_email": get_mailFromID(r.user_id),
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at
            # "images": [img.image_url for img in r.images]
        })

    return jsonify(result), 200



@review_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_review(product_id):
    user_email = get_jwt_identity()
    from app.tasks.log_task import deleate_review
    res=deleate_review.delay(product_id,user_email)
    print(res)
    return jsonify({"message": "Review deleted"}), 200



@review_bp.route("/product/<int:product_id>/rating")
def product_rating(product_id):
    avg = db.session.query(func.avg(Review.rating))\
        .filter_by(product_id=product_id)\
        .scalar()

    return jsonify({
        "product_id": product_id,
        "average_rating": round(avg or 0, 1)
    })
