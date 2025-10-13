# app/db/repositories/rankings_repo.py

import json
from typing import List, Dict, Any, Optional
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from db.models.ranking import RevvRanking

def bulk_create_rankings(db: Session, request_id: int, ranked: List[Dict[str, Any]]) -> None:
    """
    Persist top-N ranking results for a given request_id.
    Each item in ranked is expected to contain: mmv, score_percent, reason, breakdown.
    """
    rows = []
    for r in ranked:
        rows.append(
            RevvRanking(
                request_id=request_id,
                mmv=str(r.get("mmv", "")),
                score_percent=float(r.get("score_percent", 0.0)),
                reason=str(r.get("reason", "")),
                breakdown_json=json.dumps(r.get("breakdown", {}), ensure_ascii=False),
            )
        )
    if rows:
        db.add_all(rows)
        db.commit()

def list_rankings_by_request(db: Session, request_id: int, limit: int = 50) -> List[RevvRanking]:
    stmt = (
        select(RevvRanking)
        .where(RevvRanking.request_id == request_id)
        .order_by(desc(RevvRanking.score_percent))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())

def get_top_ranking_for_request(db: Session, request_id: int) -> Optional[RevvRanking]:
    stmt = (
        select(RevvRanking)
        .where(RevvRanking.request_id == request_id)
        .order_by(desc(RevvRanking.score_percent))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()

