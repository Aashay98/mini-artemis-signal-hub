import os
from celery import Celery

# Configure Celery with Redis as the broker
celery = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    include=["app.tasks"]
)

celery.conf.timezone = "UTC"
