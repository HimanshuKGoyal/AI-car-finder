import json
from sqlalchemy.orm import Session
from db.models.request import RevvRequest

def create_request(db: Session, payload: dict) -> RevvRequest:
    r = RevvRequest(payload_json=json.dumps(payload, ensure_ascii=False))
    db.add(r)
    db.commit()
    db.refresh(r)
    return r