from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
import os

# Environment Variables (Set these on your server)
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TELEGRAM_NUMERIC_ID = int(os.getenv('TELEGRAM_NUMERIC_ID'))
SESSION_STRING = os.getenv('SESSION_STRING')


# Initialize FastAPI app
app = FastAPI()


# Telegram Client Initialization
client = TelegramClient(SESSION_STRING, API_ID, API_HASH)
client.connect()


class MessageData(BaseModel):
    chat_id: int
    message: str


@app.post('/send-message/')
async def send_message(data: MessageData):
    try:
        if not client.is_user_authorized():
            client.send_code_request(TELEGRAM_NUMERIC_ID)
            raise HTTPException(status_code=401, detail="Unauthorized. Please authenticate again.")

        await client.send_message(data.chat_id, data.message)
        return {"status": "Message sent successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/status/')
async def status():
    if client.is_connected():
        return {"status": "Connected to Telegram."}
    else:
        return {"status": "Disconnected."}
