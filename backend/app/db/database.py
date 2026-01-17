"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os
from pathlib import Path

# SQLite database path
if settings.DATABASE_URL.startswith("sqlite"):
    # Extract path from sqlite:///backend/data/squire.db
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # Use absolute path for SQLite
    db_abs_path = os.path.abspath(db_path)
    engine = create_engine(f"sqlite:///{db_abs_path}", connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

