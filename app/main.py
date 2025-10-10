# reco_service/app/main.py
from fastapi import FastAPI
from app.api.v1.ranking import router as ranking_router
from app.api.v1.health import router as health_router
from app.api.v1.feedback import router as feedback_router

app = FastAPI()

app.include_router(ranking_router, prefix="/v1")
app.include_router(health_router, prefix="")
app.include_router(feedback_router, prefix="")


