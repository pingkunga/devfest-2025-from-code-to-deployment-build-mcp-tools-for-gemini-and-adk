# app/db/repositories.py
from datetime import datetime
from typing import Any, List, Literal

from bson import ObjectId

from app.db.mongo import get_db
from app.utils.time import now_utc


async def upsert_user_profile(
    uid: str,
    *,
    display_name: str | None,
    picture_url: str | None,
    status_message: str | None,
    language: str | None,
    last_seen_at: datetime | None = None,
    channel: str = "line",
    raw_profile: dict | None = None,
) -> None:
    """Insert or update a user's LINE profile + last_seen_at."""
    db = get_db()
    now = now_utc()
    update = {
        "$setOnInsert": {
            "uid": uid,
            "created_at": now,
            "channel": channel,
        },
        "$set": {
            "display_name": display_name,
            "picture_url": picture_url,
            "status_message": status_message,
            "language": language,
            "last_seen_at": last_seen_at or now,
            "updated_at": now,
        },
    }
    if raw_profile is not None:
        update["$set"]["meta"] = {"line_profile_raw": raw_profile}

    await db["users"].update_one({"uid": uid}, update, upsert=True)


async def save_message(
    uid: str,
    role: Literal["user", "assistant", "system"],
    text: str,
    ts=None,
    channel: str = "line",
    conversation_id: ObjectId | None = None,
    meta: dict[str, Any] | None = None,
) -> str:
    db = get_db()
    now = now_utc()
    doc = {
        "uid": uid,
        "role": role,
        "text": text,
        "ts": ts or now_utc(),
        "channel": channel,
        "conversation_id": conversation_id,
        "meta": meta or {},
    }
    res = await db["messages"].insert_one(doc)

    if conversation_id:
        await db["conversations"].update_one(
            {"_id": conversation_id},
            {
                "$set": {
                    "updated_at": now,
                    "last_message_at": now,
                    "last_role": role,
                    "last_text": text[:512],
                },
                "$inc": {"message_count": 1},
            },
        )

    return str(res.inserted_id)


async def get_last_messages(uid: str, n_latest: int) -> List[dict]:
    db = get_db()
    cursor = db["messages"].find({"uid": uid}).sort("ts", 1)
    docs = await cursor.to_list(length=1000)
    return docs[-n_latest:] if len(docs) > n_latest else docs


async def get_or_create_open_conversation(
    uid: str, *, title: str | None = None
) -> ObjectId:
    """Return the most recent open conversation for a uid; create if none."""
    db = get_db()
    doc = await db["conversations"].find_one(
        {"uid": uid, "status": "open"}, sort=[("updated_at", -1)]
    )
    if doc:
        return doc["_id"]

    now = now_utc()
    res = await db["conversations"].insert_one(
        {
            "uid": uid,
            "title": title or "Default thread",
            "status": "open",
            "channel": "line",
            "created_at": now,
            "updated_at": now,
            "last_message_at": None,
            "last_role": None,
            "last_text": None,
            "message_count": 0,
            "meta": {},
        }
    )
    return res.inserted_id
