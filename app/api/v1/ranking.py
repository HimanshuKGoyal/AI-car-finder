# reco_service/app/api/v1/ranking.py
from fastapi import APIRouter, Depends
from app.schemas.ranking import UserData
from app.services.recommendation import rank_cars
from app.core.rate_limit import rate_limit

router = APIRouter()

@router.post("/rank", dependencies=[Depends(rate_limit)])
def rank(payload: UserData):
    results = rank_cars(payload, top_n=5)
    return {"results": results, "count": len(results)}
