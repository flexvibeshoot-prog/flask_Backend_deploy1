from app.celery_app import celery
import time
from app.meilisearch_setup import index
from app.models import Product
from app.redis.redis_setup import redis_client
from config import Config


#Data uplode job
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="heavy_queue")
def rebuild_search_index(self):
    from app.tasks.simple_task.decimal_tofloat import serialize
    from app.tasks.simple_task.search_relates_simple_task.get_catagory import get_category_with_children
    try:
        products = Product.query.all()

        docs = [{
            "id": p.product_id,
            "name": p.name,
            "description": p.description,
            "price": serialize(p.price),
            "category":get_category_with_children(p.category_id)
        } for p in products]

        # index.delete_all_documents()
        if docs:
            index.delete_all_documents()
            index.add_documents(docs)

    finally:
        # release lock when done
        redis_client.delete(Config.LOCK_KEY)


#indexing job
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3},queue="heavy_queue")
def add_filter_attributes(self):
    print("Indexing started...")
    try:
        index.update_settings({
            "filterableAttributes": [
                "category",
                "price"
            ]
        })
        print("Indexing complited...!!!")
    except:
        print("Indexing failed...!!!")
    finally:
        # release lock when done
        redis_client.delete(Config.LOCK_KEY_INDEXING)



#Test job
@celery.task(
    name="app.tasks.heavy_task.process_heavy_task",
    queue="heavy_queue"
)
def process_heavy_task():
    time.sleep(10)
    return "Heavy task completed"
