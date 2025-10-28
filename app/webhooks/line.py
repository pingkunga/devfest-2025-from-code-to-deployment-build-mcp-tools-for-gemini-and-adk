# app/webhooks/line.py
from bson import ObjectId
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from app.config import settings
from app.db.repositories import (
    get_last_messages,
    get_or_create_open_conversation,
    save_message,
    upsert_user_profile,
)
from app.services.langgraph import build_prompt, get_agent_graph
from app.utils.line_sig import verify_line_signature
from app.utils.time import to_dt_from_ms

router = APIRouter()
_line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
_parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@router.post("/webhook")
async def webhook(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    if not verify_line_signature(settings.LINE_CHANNEL_SECRET, body, x_line_signature):
        raise HTTPException(status_code=400, detail="Invalid LINE signature")
    try:
        events = _parser.parse(body.decode("utf-8"), x_line_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    results = []
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            uid = event.source.user_id
            user_text = (event.message.text or "").strip()
            ts = to_dt_from_ms(getattr(event, "timestamp", None))

            conversation_id: ObjectId = await get_or_create_open_conversation(uid)

            await save_message(
                uid, "user", user_text, ts=ts, conversation_id=conversation_id
            )

            try:
                prof = _line_bot_api.get_profile(uid)  # sync SDK call

                profile_dict = {
                    "display_name": getattr(prof, "display_name", None),
                    "picture_url": getattr(prof, "picture_url", None),
                    "status_message": getattr(prof, "status_message", None),
                    "language": getattr(prof, "language", None),
                }
                await upsert_user_profile(
                    uid,
                    display_name=profile_dict["display_name"],
                    picture_url=profile_dict["picture_url"],
                    status_message=profile_dict["status_message"],
                    language=profile_dict["language"],
                    last_seen_at=ts,
                    channel="line",
                    raw_profile={
                        "user_id": uid,
                        **{k: v for k, v in profile_dict.items()},
                    },
                )
            except Exception:
                # Not friends yet / blocked / API error: skip silently
                pass

            history = await get_last_messages(uid, settings.N_LATEST)
            lc_messages = build_prompt(user_text, history)

            graph = await get_agent_graph()  # <— NEW: get (tool-capable) graph
            try:
                out_state = await graph.ainvoke(
                    {
                        "messages": lc_messages,
                        "uid": uid,
                        "conversation_id": conversation_id,
                    }
                )
                ai_msg = out_state["messages"][-1]
                reply_text = getattr(ai_msg, "content", str(ai_msg))
            except Exception as e:
                reply_text = f"Sorry, I hit an error running the model: {e}"

            await save_message(
                uid, "assistant", reply_text, conversation_id=conversation_id
            )
            try:
                _line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text=reply_text[:5000])
                )
            except Exception:
                reply_text += "\n\n(Note: Unable to send reply via LINE API.)"

            results.append({"uid": uid, "result": reply_text})

    return JSONResponse({"ok": True, "results": results})
