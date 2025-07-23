import os

from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

from app.config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    OPENAI_API_KEY,
)

router = APIRouter()

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)  # 新しいOpenAIクライアント


@router.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_message = event.message.text

            try:
                # ChatGPTへの問い合わせ（新API使用）
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたは親切で丁寧なLINEのアシスタントBotです。",
                        },
                        {"role": "user", "content": user_message},
                    ],
                )
                reply_text = response.choices[0].message.content.strip()

            except Exception as e:
                reply_text = f"OpenAI APIエラー: {str(e)}"

            # ユーザーに返信
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply_text)
            )

    return "OK"
