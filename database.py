from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from contextlib import contextmanager
import traceback

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class HabitDB(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    sleep_hours = Column(Float)
    water_litres = Column(Float)
    mood = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables successfully created")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        print(traceback.format_exc())
        raise
    finally:
        db.close()

def get_db_dependency():
    with get_db() as db:
        yield db