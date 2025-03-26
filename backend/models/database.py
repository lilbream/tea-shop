from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Настройка пути для Railway
DATA_DIR = Path("/data")
DATA_DIR.mkdir(exist_ok=True, parents=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()