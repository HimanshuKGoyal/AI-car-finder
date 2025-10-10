from db.base import Base
from datetime import datetime, timezone
from sqlalchemy import Column, JSON, Integer, DateTime

def now_utc():
    return datetime.now(timezone.utc)

class RevvRequest(Base):
    __tablename__ = "revv_request"
    id = Column(Integer, primary_key=True, autoincrement=True)
    payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=now_utc)
