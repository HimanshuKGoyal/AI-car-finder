from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
# from app.core.config import settings

connect_args = {}
# if settings.database_url.startswith("sqlite"):
#     # sqlite needs this when used with threaded servers
#     connect_args = {"check_same_thread": False}

class Base(DeclarativeBase):
    pass

engine = create_engine(
    "sqlite:///Torque3.db", #settings.database_url,
    future=True,
    echo=False,
    pool_pre_ping=True,
    # connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
