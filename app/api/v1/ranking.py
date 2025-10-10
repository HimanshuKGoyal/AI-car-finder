# reco_service/app/api/v1/ranking.py
from fastapi import APIRouter
from app.schemas.ranking import UserData
from app.services.recommendation import rank_cars

router = APIRouter()

@router.post("/rank")
def rank(payload: UserData):
    results = rank_cars(payload, top_n=5)
    return {"results": results, "count": len(results)}
