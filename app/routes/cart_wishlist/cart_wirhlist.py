from flask import Flask,Blueprint,jsonify,request
from app.models import User,CartItem,Wishlist
from app import db
from flask_jwt_extended import jwt_required,get_jwt_identity

cart=Blueprint('cart',__name__,url_prefix='/save_list')

@cart.route('/addto_cart', methods=['POST'])
@jwt_required()
def addto_cart():
    email = get_jwt_identity()
    data = request.get_json()

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': "User not found"}), 404

    try:
        new_cart = CartItem(
            user_id=user.user_id,
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        db.session.add(new_cart)
        db.session.commit()

        return jsonify({'message': 'Item added to cart'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Something went wrong'}), 500

    
@cart.route('/addto_wishlist', methods=['POST'])
@jwt_required()
def addto_wishlist():
    email = get_jwt_identity()
    data = request.get_json()

    if not data or 'product_id' not in data:
        return jsonify({'message': 'product_id is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    exists = Wishlist.query.filter_by(
        user_id=user.user_id,
        product_id=data['product_id']
    ).first()

    if exists:
        return jsonify({'message': 'Already in wishlist'}), 409

    try:
        wishlist_item = Wishlist(
            user_id=user.user_id,
            product_id=data['product_id']
        )
        db.session.add(wishlist_item)
        db.session.commit()

        return jsonify({'message': 'Item added to wishlist'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Something went wrong'}), 500

