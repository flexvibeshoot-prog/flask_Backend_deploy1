from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, CartItem, Wishlist, Product,ProductImage
from app import db


get_cart_item=Blueprint('get_cart_item',__name__,url_prefix='/get_list')


@get_cart_item.route("/cart", methods=["GET"])
@jwt_required()
def get_cart_items():
    user_email = get_jwt_identity()

    from app.tasks.simple_task.get_userID import get_userid
    user_id = get_userid(user_email)

    cart_items =CartItem.query.filter_by(user_id=user_id).all()

    result = []
    total_price = 0

    for cart in cart_items:
        product = Product.query.get(cart.product_id)
        product_img=ProductImage.query.filter_by(product_id=product.product_id).first()
        subtotal = cart.quantity * product.price
        total_price += subtotal

        result.append({
            "cart_id": cart.cart_item_id,
            "product_id": product.product_id,
            "product_name": product.name,
            "price": product.price,
            "quantity": cart.quantity,
            "subtotal": subtotal,
            "image": product_img.image_url if product_img else None
        })

    return jsonify({
        "items": result,
        "total_price": total_price
    }), 200



@get_cart_item.route("/wishlist", methods=["GET"])
@jwt_required()
def get_wish_items():
    user_email = get_jwt_identity()

    from app.tasks.simple_task.get_userID import get_userid
    user_id = get_userid(user_email)

    wishlist_items =Wishlist.query.filter_by(user_id=user_id).all()

    result = []
    total_price = 0

    for cart in wishlist_items:
        product = Product.query.get(cart.product_id)
        product_img=ProductImage.query.filter_by(product_id=product.product_id).first()

        result.append({
            "wishlist_id": cart.wishlist_id,
            "product_id": product.product_id,
            "product_name": product.name,
            "price": product.price,
            "image": product_img.image_url if product_img else None,
            "added_on": cart.added_at
        })

    return jsonify({
        "items": result,
        "total_price": total_price
    }), 200