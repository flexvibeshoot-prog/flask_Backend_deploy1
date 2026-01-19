from app.models import User

def get_userid(email):
    user=User.query.filter_by(email=email).first()

    if not user:
        return -1
    return user.user_id

def get_mailFromID(user_id):
    user=User.query.filter_by(user_id=user_id).first()
    if user:
        return user.email
    return '-1'