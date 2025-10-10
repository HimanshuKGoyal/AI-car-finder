from db.base import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

def now_utc():
    return datetime.now(timezone.utc)

class RevvFeedback(Base):
    __table__ = "revv_feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    mmv = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    created_at = Column(DateTime, index=True, default=now_utc)

    __table_args__ = (
        CheckConstraint("action IN ('save','dismiss')", name="ck_feedback_action"),
    )

    
