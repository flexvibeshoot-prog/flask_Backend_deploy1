from decimal import Decimal

def serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    return value
