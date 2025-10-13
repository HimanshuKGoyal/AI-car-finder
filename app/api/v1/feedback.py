from fastapi import APIRouter
from app.schemas.feedback import Feedback

router = APIRouter()

@router.post("/feedback")
def feedback(data: Feedback):
    print("Feedback: ", data.model_dump())
    return {"OK": True}
