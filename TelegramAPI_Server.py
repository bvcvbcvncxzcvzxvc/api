from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

# متغیرهای محیطی (این مقادیر باید روی سرور تنظیم شوند)
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TELEGRAM_NUMERIC_ID = int(os.getenv('TELEGRAM_NUMERIC_ID'))
SESSION_STRING = os.getenv('SESSION_STRING')

# راه‌اندازی اپلیکیشن FastAPI
app = FastAPI()

# مقداردهی اولیه‌ی کلاینت تلگرام با استفاده از StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    await client.connect()
    if not await client.is_user_authorized():
        raise HTTPException(status_code=401, detail="Unauthorized. Please authenticate again.")

# مدل داده پیام – در اینجا تنها فیلد message نیاز است
class MessageData(BaseModel):
    message: str

@app.post('/send-message/')
async def send_message(data: MessageData):
    try:
        # استفاده از TELEGRAM_NUMERIC_ID از متغیر محیطی به جای دریافت chat_id از کلاینت
        await client.send_message(TELEGRAM_NUMERIC_ID, data.message)
        return {"status": "Message sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/status/')
async def status():
    if client.is_connected():
        return {"status": "Connected to Telegram."}
    else:
        return {"status": "Disconnected."}
