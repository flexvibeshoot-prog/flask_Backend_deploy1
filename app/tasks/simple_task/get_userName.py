from app.models import User

def get_userName(email):
    user=User.query.filter_by(email=email).first()

    if not user:
        return None
    return user.full_name