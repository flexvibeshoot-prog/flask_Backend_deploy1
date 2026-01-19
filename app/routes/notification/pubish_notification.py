from app.redis.redis_setup import redis_client as r

def send(user_email,message):
    print('published.')
    r.publish(f"user:{user_email}", message)
    return "sent"