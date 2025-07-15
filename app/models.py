from sqlalchemy import DateTime, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()

class Tick(Base):
    __tablename__ = "ticks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    ts = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created = Column(DateTime)


class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    signal = Column(String)
    created = Column(DateTime)