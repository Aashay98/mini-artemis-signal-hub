from app.celery_worker import celery
from app.models import Session, Tick, Signal
from sqlalchemy import create_engine
import redis
import time

# Redis and Postgres configurations
redis_client = redis.Redis(host='redis', port=6379, db=0)
engine = create_engine("postgresql://postgres:postgres@localhost:5432/mini_artemis")

@celery.task
def process_ticks(tick):
    """Process each tick to calculate SMA crossover."""
    # Store tick in Postgres (for persistence)
    with Session(engine) as session:
        new_tick = Tick(**tick)
        session.add(new_tick)
        session.commit()

    # Store signal in Redis and Postgres
    signal = calculate_sma_crossover(tick)
    redis_client.set(f"signal:{tick['symbol']}", signal)
    store_signal_in_db(signal)

def calculate_sma_crossover(tick):
    """Dummy function to calculate 20/50 SMA crossover."""
    return "BUY" if tick["close"] > 50 else "SELL"

def store_signal_in_db(signal):
    """Store trading signal in Postgres."""
    with Session(engine) as session:
        new_signal = Signal(symbol=signal["symbol"], signal=signal["signal"])
        session.add(new_signal)
        session.commit()
