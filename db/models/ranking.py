# from db.base import Base
# from datetime import datetime, timezone
# from sqlalchemy import Column, JSON, ForeignKey, Integer, DateTime

# def now_utc():
#     return datetime.now(timezone.utc)

# class RecoResults(Base):
#     __tablename__ = "recommendation_results"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     request_id = Column(Integer, ForeignKey)
#     payload_json = Column(JSON)
#     created_at = Column(DateTime, index=True, default=now_utc)

from sqlalchemy import DateTime, Integer, Text, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class RevvRanking(Base):
    __tablename__ = "revv_rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)

    mmv: Mapped[str] = mapped_column(Text, nullable=False)  # Make-Model-Variant identifier
    score_percent: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    breakdown_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())