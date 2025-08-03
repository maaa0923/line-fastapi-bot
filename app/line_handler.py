import os

from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
from app.firestore import save_user
from app.firestore import get_all_user_ids

from app.config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    OPENAI_API_KEY,
)

router = APIRouter()

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)  # 新しいOpenAIクライアント

async def generate_question() -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは英語の先生です。英語学習者に1日1問、英語で答えられる質問を出題します。"
                    "質問はシンプルで回答しやすいもので、日常生活に関するトピックにしてください。"
                    "例: 'What did you eat for breakfast today?' のような形式。"
                    "出力は英語の質問文のみ1つ。"
                ),
            },
        ],
    )
    return response.choices[0].message.content.strip()

@router.get("/daily")
async def send_daily_question():
    try:
        # 質問を生成
        question = await generate_question()

        # Firestore に保存された全ユーザーに送信
        user_ids = get_all_user_ids()
        for user_id in user_ids:
            line_bot_api.push_message(user_id, TextSendMessage(text=question))

        return {"status": "success", "message": "Question sent", "question": question}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# callback はユーザーの返信を処理
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
            user_id = event.source.user_id  # ← ユーザーIDを取得
            save_user(user_id)              # ← Firestore に保存

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "あなたは英語の先生です。"
                                "学習者からの英語の回答に対して、わかりやすく日本語で丁寧にフィードバックをします。"
                                "文法・単語・自然さ・褒め言葉なども含めてください。"
                            ),
                        },
                        {"role": "user", "content": user_message},
                    ],
                )
                reply_text = response.choices[0].message.content.strip()
            except Exception as e:
                reply_text = f"OpenAI APIエラー: {str(e)}"

            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply_text)
            )

    return "OK"

