# search_lock.py
from app.redis.redis_setup import redis_client
from config import Config

def enqueue_once(task):
    # nx=True → only if key does NOT exist
    # ex=600  → auto expire in 10 min
    if redis_client.set(Config.LOCK_KEY, "1", nx=True, ex=600):
        task.delay()
        return True   # accepted
    return False      # rejected


def indexing_once(task):
    # nx=True → only if key does NOT exist
    # ex=600  → auto expire in 10 min
    if redis_client.set(Config.LOCK_KEY_INDEXING, "1", nx=True, ex=600):
        task.delay()
        return True   # accepted
    return False      # rejected
