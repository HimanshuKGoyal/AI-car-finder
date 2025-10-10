# app/db/repositories/feedback_repo.py

from sqlalchemy.orm import Session
from db.models.feedback import RevvFeedback

def create_feedback(db: Session, request_id: int, mmv: str, action: str) -> RevvFeedback:
    fb = RevvFeedback(request_id=request_id, mmv=mmv, action=action)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
