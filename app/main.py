# reco_service/app/main.py
from fastapi import FastAPI
from db.base import Base, engine
from db.seed import seed_makes_if_empty
from contextlib import asynccontextmanager
from app.api.v1.ranking import router as ranking_router
from app.api.v1.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initiating DB Tables Creation on engine: ", engine.url)
    Base.metadata.create_all(bind=engine)
    print("Done. If using SQLite, local_db.sqlite should now exist.")
    seed_makes_if_empty()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(ranking_router, prefix="/v1")
app.include_router(health_router, prefix="")


