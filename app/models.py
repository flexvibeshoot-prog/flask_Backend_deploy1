from datetime import datetime
from app import db

# ===============================
# USER MANAGEMENT
# ===============================

class Role(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship("User", back_populates="role", cascade="all, delete")


class Admin(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id", ondelete="CASCADE"), default=1)
    is_active = db.Column(db.Boolean, default=False)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)

    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=True)

    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_provider_id = db.Column(db.String(255), nullable=True)

    avatar_url = db.Column(db.String(255), nullable=True)

    phone = db.Column(db.String(15))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id", ondelete="CASCADE"), default=2)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)

    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

    role = db.relationship("Role", back_populates="users")
    addresses = db.relationship("Address", back_populates="user", cascade="all, delete")
    cart_items = db.relationship("CartItem", back_populates="user", cascade="all, delete")
    wishlists = db.relationship("Wishlist", back_populates="user", cascade="all, delete")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")


class Address(db.Model):
    __tablename__ = "addresses"
    address_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="addresses")
    orders = db.relationship("Order", back_populates="address", cascade="all, delete")


class Pincode(db.Model):
    __tablename__ = "pincodes"

    pincode = db.Column(db.String(6), primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_serviceable = db.Column(db.Boolean, default=True)

# ===============================
# PRODUCT CATALOG
# ===============================

class Category(db.Model):
    __tablename__ = "categories"
    category_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.category_id", ondelete="CASCADE"),nullable=True)

    parent = db.relationship("Category", remote_side=[category_id], backref="subcategories")
    products = db.relationship("Product", back_populates="category", cascade="all, delete")


class Brand(db.Model):
    __tablename__ = "brands"
    brand_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship("Product", back_populates="brand", cascade="all, delete")


class Product(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id", ondelete="CASCADE"))
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.brand_id", ondelete="CASCADE"))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", back_populates="products")
    brand = db.relationship("Brand", back_populates="products")
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete")
    inventory = db.relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete")
    cart_items = db.relationship("CartItem", back_populates="product", cascade="all, delete")
    wishlists = db.relationship("Wishlist", back_populates="product", cascade="all, delete")
    order_items = db.relationship("OrderItem", back_populates="product", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="product", cascade="all, delete")


class ProductImage(db.Model):
    __tablename__ = "product_images"
    image_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    image_url = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)

    product = db.relationship("Product", back_populates="images")


class Inventory(db.Model):
    __tablename__ = "inventory"
    inventory_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    quantity = db.Column(db.Integer, default=0)

    product = db.relationship("Product", back_populates="inventory")


# ===============================
# CART & WISHLIST
# ===============================

class CartItem(db.Model):
    __tablename__ = "cart_items"
    cart_item_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")


class Wishlist(db.Model):
    __tablename__ = "wishlists"
    wishlist_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="wishlists")
    product = db.relationship("Product", back_populates="wishlists")


# ===============================
# ORDERS & PAYMENTS
# ===============================

class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.address_id", ondelete="CASCADE"))
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50), default="Pending")
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=True)
    razorpay_payment_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="orders")
    address = db.relationship("Address", back_populates="orders")
    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete")
    payments = db.relationship("Payment", back_populates="order", cascade="all, delete")
    shipment = db.relationship("Shipment", back_populates="order", uselist=False, cascade="all, delete")


class OrderStatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    status = db.Column(db.String(50))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id", ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    order = db.relationship("Order", back_populates="order_items")
    product = db.relationship("Product", back_populates="order_items")


class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"
    method_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    payments = db.relationship("Payment", back_populates="method", cascade="all, delete")


class Payment(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id", ondelete="CASCADE"))
    method_id = db.Column(db.Integer, db.ForeignKey("payment_methods.method_id", ondelete="CASCADE"))
    amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.String(50), default="Pending")
    transaction_id = db.Column(db.String(100))
    razorpay_payment_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="payments")
    method = db.relationship("PaymentMethod", back_populates="payments")


# ===============================
# REVIEWS
# ===============================

class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
    images = db.relationship("ReviewImage", back_populates="review", cascade="all, delete")


class ReviewImage(db.Model):
    __tablename__ = "review_images"
    review_image_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.review_id", ondelete="CASCADE"))
    image_url = db.Column(db.String(255))

    review = db.relationship("Review", back_populates="images")


# ===============================
# SHIPPING & LOGISTICS
# ===============================

class Shipment(db.Model):
    __tablename__ = "shipments"
    shipment_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id", ondelete="CASCADE"))
    tracking_number = db.Column(db.String(100))
    courier_name = db.Column(db.String(100))
    shipment_status = db.Column(db.String(50), default="Processing")
    shipped_date = db.Column(db.DateTime, nullable=True)
    delivered_date = db.Column(db.DateTime, nullable=True)

    order = db.relationship("Order", back_populates="shipment")


# ===============================
# PROMOTIONS
# ===============================

class Coupon(db.Model):
    __tablename__ = "coupons"
    coupon_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2))
    max_discount = db.Column(db.Numeric(10, 2))
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)


# ================================
# NOTIFICATION
#=================================

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    releted_link = db.Column(db.String(255))
    message = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Firebase Push Notification Tokens
class PushToken(db.Model):
    __tablename__ = "push_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    token = db.Column(db.String(255), unique=True, nullable=False)
    device_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

