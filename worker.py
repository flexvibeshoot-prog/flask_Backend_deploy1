from app.celery_app import celery

# 🔥 REGISTER ALL TASK MODULES
import app.tasks.Registermessaging_task
import app.tasks.heavy_task
import app.tasks.log_task

if __name__ == "__main__":
    celery.start()

