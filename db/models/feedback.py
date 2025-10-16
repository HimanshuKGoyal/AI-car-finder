from sqlalchemy import DateTime, Integer, Text, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class RevvFeedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    mmv: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)  # "save" | "dismiss"
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("action IN ('save','dismiss')", name="ck_feedback_action"),
    )
