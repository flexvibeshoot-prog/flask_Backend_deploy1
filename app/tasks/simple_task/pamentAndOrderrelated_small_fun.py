from app.models import Order,OrderItem,PaymentMethod,Payment,Product,Address,User

def get_items_from_order_id(order_id):
    order_items = (
        OrderItem.query
        .filter_by(order_id=order_id)
        .all()
    )

    items = []
    for order_item in order_items:
        product = Product.query.get(order_item.product_id)

        items.append({
            "name": product.name if product else "Unknown",
            "quantity": order_item.quantity,
            "price": order_item.price
        })

    return items



def get_Address_using_order_id(order_id):
    order=Order.query.filter_by(order_id=order_id).first()
    address=Address.query.filter_by(address_id=order.address_id).first()
    sort_address=dict(city=address.city,state=address.state,country=address.country,postal_code=address.postal_code)
    return sort_address


def get_product_id_from_order_id(order_id):
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    products_info = []
    for order in order_items:
        order_info = dict(
            product_id = order.product_id,
            quantity = order.quantity
        )
        products_info.append(order_info)
    return products_info



def order_id_from_razorpay_order_id(razorpay_order_id,razorpay_payment_id):
    order = Order.query.filter_by(razorpay_order_id=razorpay_order_id).first()
    if order:
        payment=Payment.query.filter_by(order_id=order.order_id).first()
        payment.razorpay_payment_id = razorpay_payment_id
        payment.payment_status = "PAID"
        order.razorpay_payment_id = razorpay_payment_id
        order.status = "Confirmed"
        from app import db
        db.session.commit()
        return order.order_id
    return None
        


def get_email_from_razorpay_payment_id(razorpay_payment_id):
    order = Order.query.filter_by(razorpay_payment_id=razorpay_payment_id).first()
    if order:
        user = User.query.filter_by(user_id=order.user_id).first()
        return user.email
    return None