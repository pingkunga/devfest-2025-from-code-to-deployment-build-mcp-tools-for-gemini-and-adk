# app/factory.py
from fastapi import FastAPI

from app.config import settings  # noqa
from app.db.indexes import ensure_indexes
from app.webhooks.line import router as line_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="LINE x Gemini x ADK",
        version="1.0.0",
    )

    # Routers
    app.include_router(line_router, prefix="/line", tags=["line"])

    # Startup hooks
    @app.on_event("startup")
    async def _startup():
        await ensure_indexes()

    return app
