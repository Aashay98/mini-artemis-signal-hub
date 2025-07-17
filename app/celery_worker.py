from celery import Celery

# Configure Celery with Redis as the broker
celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks"]
)

celery.conf.timezone = "UTC"
