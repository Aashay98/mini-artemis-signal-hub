from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()

class Tick(Base):
    __tablename__ = "ticks"
    #TODO: Implement the Tick model with necessary fields