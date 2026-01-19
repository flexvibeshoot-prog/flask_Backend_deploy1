from app.models import Order,Address,Pincode
from datetime import datetime, timedelta, date


def transit_days_from_distance(distance_km):
    if distance_km <= 50:
        return 1
    elif distance_km <= 200:
        return 2
    elif distance_km <= 500:
        return 3
    else:
        return 5


def get_next_sunday(d):
    days_ahead = 6 - d.weekday()  # Monday=0, Sunday=6
    if days_ahead < 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def estimate_delivery_date(distance_km, order_date=None):
    if not order_date:
        order_date = date.today()

    transit_days = transit_days_from_distance(distance_km)

    # Date when parcel reaches local hub
    ready_date = order_date + timedelta(days=transit_days)

    # Delivery happens only on Sunday
    delivery_date = get_next_sunday(ready_date)

    return delivery_date



def get_delivery_date_estimate(order_id):
    from config import Config
    from app.tasks.location.distance_calc import calculate_distance_km
    order=Order.query.filter_by(order_id=order_id).first()
    address=Address.query.filter_by(address_id=order.address_id).first()
    pincode=Pincode.query.filter_by(pincode=address.postal_code).first()
    if pincode:
        distance=calculate_distance_km(Config.ADMIN_LAT,Config.ADMIN_LONG,pincode.latitude,pincode.longitude)
        return estimate_delivery_date(distance)
    else:
        from app.tasks.location.get_lat_long import geocode_address
        lat,long=geocode_address(address.postal_code)
        if lat and long:
            from app.tasks.log_task import set_pin_info
            set_pin_info.delay(address.postal_code,lat,long,True)
            distance=calculate_distance_km(Config.ADMIN_LAT,Config.ADMIN_LONG,lat,long)
            return estimate_delivery_date(distance)