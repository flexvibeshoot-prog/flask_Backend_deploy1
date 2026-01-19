from flask import Blueprint,jsonify,request
from app import db
from app.models import Brand, Category,Product,ProductImage,Inventory
import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask_jwt_extended import jwt_required

product = Blueprint('product', __name__, url_prefix='/product')

# 🆕 ADD PRODUCT
@product.route('/add_category', methods=['POST'])
def add_category():
    try:
        data = request.get_json()
        name = data.get('name')
        parent_id = data.get('parent_id')

        new_category = Category(name=name, parent_id=parent_id)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            "message": "Category added successfully",
            "category_id": new_category.category_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product.route('/add_brand', methods=['POST'])
def add_brand():
    try:
        data = request.get_json()
        name = data.get('name')

        # Assuming Brand model exists
        new_brand = Brand(name=name)
        db.session.add(new_brand)
        db.session.commit()

        return jsonify({
            "message": "Brand added successfully",
            "brand_id": new_brand.brand_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product.route('/add_product', methods=['POST'])
def add_product():
    try:
        # Get non-file fields from request.form
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        category_id = request.form.get('category_id')
        brand_id = request.form.get('brand_id')
        discount = request.form.get('discount')
        is_active = request.form.get('is_active')
        if isinstance(is_active, str):
            is_active = is_active.lower() == "true"

        # Get the image file
        images = request.files.getlist('image')

        # Upload image to Cloudinary if provided
        uploaded_urls = []
        uploaded_public_ids = []

        if not images or len(images) == 0:
            return jsonify({"message": "At least one image is required"}), 400
        
        for img in images:
            upload_result = cloudinary.uploader.upload(img, folder="products/")
            uploaded_urls.append(upload_result.get('secure_url'))
            uploaded_public_ids.append(upload_result.get('public_id'))

        
        # Create new product
        new_product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            brand_id=brand_id,
            discount=discount,
            is_active=is_active,
        )

        db.session.add(new_product)
        db.session.flush()  # Get product_id before commit

        inventory=Inventory(
            product_id=new_product.product_id,
            quantity=stock_quantity
        )
        db.session.add(inventory)
        db.session.commit()

        return jsonify({
            "message": "Product added successfully",
            "product_id": new_product.product_id,
            "image_urls": uploaded_urls
        }), 201
    
    except Exception as e:
        # If fail → delete all uploaded images
        for pid in uploaded_public_ids:
            cloudinary.uploader.destroy(pid)

        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@product.route('/add_image', methods=['POST'])
def add_image():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        image_urls = data.get('image_urls')  # list of URLs

        if not product_id or not image_urls:
            return jsonify({"message": "product_id and image_urls are required"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Save each image URL
        for url in image_urls:
            new_image = ProductImage(product_id=product_id, image_url=url)
            db.session.add(new_image)

        db.session.commit()

        return jsonify({
            "message": "Images added successfully",
            "count": len(image_urls)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product.route('/get_products', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        per_page = 10

        if page < 1:
            return jsonify({"message": "Page number must be at least 1"}), 400

        products = (
            Product.query
            .order_by(Product.created_at.desc())
            .all()
        )
        total = len(products)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = products[start:end]
        
        product_list = []
        for product in paginated:
            images = ProductImage.query.filter_by(product_id=product.product_id).all()
            inventory = Inventory.query.filter_by(product_id=product.product_id).first()
            product_data = {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "inventory": inventory.quantity if inventory else 0,
                "category_id": product.category_id,
                "brand_id": product.brand_id,
                "discount": str(product.discount),
                "is_active": product.is_active,
                'images': [image.image_url for image in images]
            }
            product_list.append(product_data)
        return jsonify(product_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@product.route('get_product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)   # fetch using primary key

    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    images=ProductImage.query.filter_by(product_id=product_id).all()
    # print(images)
    image_list = [
        img.image_url
        for img in images
    ]
    return jsonify({
        "id": product.product_id,
        "name": product.name,
        "price": product.price,
        "description": product.description,
        'imges':image_list
    }), 200


@product.route('/get_multiple', methods=['POST'])
def get_multiple_products():
    data = request.get_json()
    ids = data.get("ids")

    if not ids or not isinstance(ids, list):
        return jsonify({"error": "ids must be a list"}), 400
    
    if len(ids)==0:
        return jsonify({'message':'Invalid product..'})

    products = Product.query.filter(Product.product_id.in_(ids)).all()

    result = []
    for p in products:
        images=ProductImage.query.filter_by(product_id=p.product_id).all()
        image_list = [
            img.image_url
            for img in images
        ]
        result.append({
            "id": p.product_id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            'images':image_list
        })

    return jsonify({"products": result}), 200