from app.models import Product,Inventory,PaymentMethod,Order

def calculate_total_ammount(product_id,quantity):
    product=Product.query.filter_by(product_id=product_id).first()
    inventory=Inventory.query.filter_by(product_id=product_id).first()

    if inventory.quantity<quantity:
        return -1
    return product.price*quantity

def get_payment_method_id(method_name):
    new_method=PaymentMethod.query.filter_by(name=method_name).first()
    if not new_method:
        return -1
    return new_method.method_id

def get_order_amount(order_id):
    order=Order.query.filter_by(order_id=order_id).first()
    if not order:
        return -1
    return order.total_amount
