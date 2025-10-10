from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os


class Base(DeclarativeBase):
    pass

def get_database_url() -> str: 
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    return "sqlite:///car.db"

engine = create_engine(get_database_url(), 
    echo=True, 
    future=True
)

SessionLocal = sessionmaker(autocommit=False, 
    autoflush=False, 
    bind=engine,
    future=True
)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()