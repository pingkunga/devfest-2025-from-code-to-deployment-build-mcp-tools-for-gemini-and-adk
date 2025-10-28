# app/db/schemas.py
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class UserIn(BaseModel):
    uid: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: Optional[str] = None
    last_seen_at: datetime
    channel: str = "line"


class MessageIn(BaseModel):
    uid: str
    role: Literal["user", "assistant", "system", "tool"]
    text: str
    ts: datetime
    channel: str = "line"
    conversation_id: str | None = None
    meta: dict[str, Any] | None = None


class MessageOut(BaseModel):
    id: str = Field(alias="_id")
    uid: str
    role: Literal["user", "assistant", "system", "tool"]
    text: str
    ts: datetime
    channel: str
    conversation_id: str | None = None
    meta: dict[str, Any] | None = None


class ConversationIn(BaseModel):
    uid: str
    title: Optional[str] = "Default thread"
    status: Literal["open", "closed"] = "open"
    channel: str = "line"
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    last_role: Optional[Literal["user", "assistant", "tool", "system"]] = None
    last_text: Optional[str] = None
    message_count: int = 0
    meta: dict[str, Any] | None = None
