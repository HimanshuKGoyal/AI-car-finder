# app/db/repositories/rankings_repo.py

import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from db.models.ranking import RevvRanking

def bulk_create_rankings(db: Session, request_id: int, ranked: List[Dict[str, Any]]) -> None:
    rows = []
    for r in ranked:
        rows.append(
            RevvRanking(
                request_id=request_id,
                mmv=r["mmv"],
                score_percent=float(r["score_percent"]),
                reason=r.get("reason", ""),
                breakdown_json=json.dumps(r.get("breakdown", {}), ensure_ascii=False),
            )
        )
    db.add_all(rows)
    db.commit()
