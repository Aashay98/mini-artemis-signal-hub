from app.celery_worker import celery
from sqlalchemy import create_engine
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)
engine = create_engine("postgresql://user:password@postgres:5432/mini_artemis")

@celery.task
def process_ticks(tick):
    #TODO: Implement the logic to process each tick
    """Process each tick to calculate SMA crossover."""
    pass