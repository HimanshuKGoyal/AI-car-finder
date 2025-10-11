import json
from typing import Optional, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from db.models.request import RevvRequest

def create_request(db: Session, payload: Dict[str, Any]) -> RevvRequest:
    """Persist the incoming payload and return the Request row."""
    r = RevvRequest(payload_json=json.dumps(payload, ensure_ascii=False))
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def get_request(db: Session, request_id: int) -> Optional[RevvRequest]:
    stmt = select(RevvRequest).where(RevvRequest.id == request_id)
    return db.execute(stmt).scalar_one_or_none()

def list_recent_requests(db: Session, limit: int = 50) -> List[RevvRequest]:
    stmt = select(RevvRequest).order_by(desc(RevvRequest.created_at)).limit(limit)
    return list(db.execute(stmt).scalars().all())
