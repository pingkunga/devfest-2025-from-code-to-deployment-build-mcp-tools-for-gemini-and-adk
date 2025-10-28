# app/db/indexes.py
from pymongo import ASCENDING

from app.db.mongo import get_db


async def ensure_indexes():
    db = get_db()
    await db["messages"].create_index([("uid", ASCENDING), ("ts", ASCENDING)])
    await db["users"].create_index("uid", unique=True)
    await db["conversations"].create_index(
        [("uid", ASCENDING), ("created_at", ASCENDING)]
    )
