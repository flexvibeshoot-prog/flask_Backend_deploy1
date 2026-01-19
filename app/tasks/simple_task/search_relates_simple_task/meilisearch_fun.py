# search_health.py
from app.meilisearch_setup import index

def search_ready():
    try:
        index.get_stats()
        return True
    except:
        return False