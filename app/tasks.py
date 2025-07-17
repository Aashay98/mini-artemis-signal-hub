import os
from dotenv import load_dotenv
from app.celery_worker import celery
from sqlalchemy import create_engine, desc, select
import redis
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
from app.models import Signal, Tick
load_dotenv()

# Redis and Postgres configurations
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
engine = create_engine(os.getenv("POSTGRES_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery.task
def process_batch_ticks(ticks):
    print(ticks)
    db: Session = SessionLocal()
    tick_models = [Tick(**tick.dict()) for tick in ticks]
    db.add_all(tick_models)
    db.commit()
    db.close()

    # group by symbol and enqueue SMA calc
    symbols = set(tick['symbol'] for tick in ticks)
    for sym in symbols:
        calculate_sma.delay(sym)

@celery.task
def calculate_sma(symbol: str):
    db: Session = SessionLocal()
    # Fetch data for SMA calculation
    sma_20, sma_50 = compute_sma(symbol, db)
    signal = classify_sma(sma_20, sma_50)

    # Save signal to Redis
    redis_key = f"signal:{symbol}"
    redis_value = {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "signal": signal,
        "sma_20": sma_20,
        "sma_50": sma_50,
    }
    redis_client.publish("signal_channel", str(redis_value))
    redis_client.set(redis_key, str(redis_value))

    # Save to Postgres
    new_signal = Signal(symbol=symbol, timestamp=datetime.utcnow(), signal=signal)
    db.add(new_signal)
    db.commit()
    db.close()
    
def compute_sma(symbol: str, db: Session):
    """Compute 20/50 SMA from recent ticks"""
    stmt = (
        select(Tick)
        .where(Tick.symbol == symbol)
        .order_by(desc(Tick.ts))
        .limit(50)
    )
    result = db.execute(stmt).scalars().all()

    closes = [tick.close for tick in result]
    if len(closes) < 20:
        return None, None  # Not enough data

    sma_20 = sum(closes[:20]) / 20
    sma_50 = sum(closes) / len(closes)

    return round(sma_20, 4), round(sma_50, 4)

def classify_sma(sma_20, sma_50):
    """Classify SMA crossover direction"""
    if sma_20 is None or sma_50 is None:
        return "HOLD"
    if sma_20 > sma_50:
        return "BUY"
    elif sma_20 < sma_50:
        return "SELL"
    return "HOLD"