import json
import os
from uuid import uuid4

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

load_dotenv()

app = FastAPI()

# LINE Bot configuration
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN must be set")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/webhook")
async def webhook(request: Request):
    """LINE Messaging API webhook endpoint"""
    # Get X-Line-Signature header value
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        raise HTTPException(
            status_code=400, detail="X-Line-Signature header is missing"
        )

    # Get request body as text
    body = await request.body()
    body = body.decode()

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """Handle text message events"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Get the text from the user
        user_message = event.message.text
        print("user_message : ", user_message)

        # ----- get response via a2a -----
        # reply_text = f"You said: {user_message}"
        reply_text = call_agent(user_message)
        print("reply_text : ", reply_text)
        # --------------------------------

        # Reply to the user
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=reply_text)]
            )
        )


# adk
def call_agent(user_message: str) -> str:
    agent_name = "agent_a"
    session_id = str(uuid4())

    base_url = "http://localhost:8000"
    endpoint = f"/apps/{agent_name}/users/u_123/sessions/{session_id}"
    url = base_url + endpoint

    try:
        # init session
        payload = {"state": {"key1": "value1", "key2": 42}}
        response_init = requests.post(url, data=json.dumps(payload))
        print(
            f"Session initialization successful. Status Code: {response_init.status_code}"
        )

        # submit prompt
        agent_payload = {
            "app_name": agent_name,
            "user_id": "u_123",
            "session_id": session_id,
            "new_message": {"role": "user", "parts": [{"text": user_message}]},
        }
        response_submit = requests.post(
            f"{base_url}/run", data=json.dumps(agent_payload)
        )
        print(
            f"Prompt submission successful. Status Code: {response_submit.status_code}"
        )

        return response_submit.json()[-1]["content"]["parts"][0]["text"]

    except Exception as e:
        print(f"Error during session initialization: {e}")
