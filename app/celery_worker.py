from celery import Celery

# Configure Celery with Redis as the broker
celery = Celery("worker", broker="redis://redis:6379/0")

celery.conf.timezone = "UTC"
