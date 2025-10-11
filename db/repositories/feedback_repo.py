from typing import List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from db.models.feedback import RevvFeedback

def create_feedback(db: Session, request_id: int, mmv: str, action: str) -> RevvFeedback:
    """Insert a feedback row: action ∈ {'save','dismiss'}."""
    fb = RevvFeedback(request_id=request_id, mmv=mmv, action=action)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def list_feedback_by_request(db: Session, request_id: int, limit: int = 100) -> List[RevvFeedback]:
    stmt = (
        select(RevvFeedback)
        .where(RevvFeedback.request_id == request_id)
        .order_by(desc(RevvFeedback.created_at))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
