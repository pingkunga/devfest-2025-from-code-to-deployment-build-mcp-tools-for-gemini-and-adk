# app/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


def get_db():
    client = get_client()
    # If your URI includes the db name, this returns it; otherwise set it explicitly
    return client["chat"]
