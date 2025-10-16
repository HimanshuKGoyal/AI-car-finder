from sqlalchemy import DateTime, Integer, Text, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class RevvRanking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)

    mmv: Mapped[str] = mapped_column(Text, nullable=False)
    score_percent: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    breakdown_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
