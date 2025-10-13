# reco_service/app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import setup_cors, SecurityHeadersMiddleware
from app.api.v1.ranking import router as ranking_router
from app.api.v1.feedback import router as feedback_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

setup_cors(app, settings.CORS_ALLOW_ORIGINS)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(ranking_router, prefix=settings.API_PREFIX)
app.include_router(feedback_router, prefix="")

# Health check
@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.ENV}
