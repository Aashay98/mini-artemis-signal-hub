from app.celery_worker import celery
from sqlalchemy import create_engine, text
import redis

# Redis and Postgres configurations
redis_client = redis.Redis(host='redis', port=6379, db=0)
engine = create_engine("postgresql://postgres:postgres@localhost:5432/mini_artemis")

@celery.task
def process_batch_ticks(ticks):
    conn = engine.connect()
    for tick in ticks:
        insert_stmt = text("""
            INSERT INTO ticks (symbol, ts, open, high, low, close, volume)
            VALUES (:symbol, :ts, :open, :high, :low, :close, :volume)
        """)
        conn.execute(insert_stmt, **tick)
    conn.commit()

    # group by symbol and enqueue SMA calc
    symbols = set(tick['symbol'] for tick in ticks)
    for sym in symbols:
        calculate_sma.delay(sym)
    conn.close()

@celery.task
def calculate_sma(tick):
    """Dummy function to calculate 20/50 SMA crossover."""
    return "BUY" if tick["close"] > 50 else "SELL"
