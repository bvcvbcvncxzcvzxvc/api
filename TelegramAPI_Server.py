import os
import asyncio
import threading
import logging
from flask import Flask, jsonify
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# تنظیمات Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/config')
def get_config():
    try:
        telegram_username = os.environ["TELEGRAM_USERNAME"]
        telegram_initial_message = os.environ["TELEGRAM_INITIAL_MESSAGE"]
    except KeyError as e:
        logging.error(f"Missing environment variable: {e}")
        return jsonify({"error": f"Missing variable {e}"}), 500

    return jsonify({
        "TELEGRAM_USERNAME": telegram_username,
        "TELEGRAM_INITIAL_MESSAGE": telegram_initial_message
    })

# خواندن اطلاعات حساس از Environment Variables (بدون مقدار پیش‌فرض)
try:
    API_ID = int(os.environ["TELEGRAM_API_ID"])
    API_HASH = os.environ["TELEGRAM_API_HASH"]
    SESSION_STRING = os.environ["TELEGRAM_SESSION"]
    REPLY_MESSAGE = os.environ["TELEGRAM_REPLY_MESSAGE"]
except KeyError as e:
    logging.error(f"Missing environment variable: {e}")
    raise

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage)
async def auto_reply(event):
    if event.out:
        return
    try:
        sender = await event.get_sender()
        sender_username = sender.username if sender else "نامشخص"
        logging.info(f"Received message from {sender_username}: {event.message.text}")
        await event.reply(REPLY_MESSAGE)
        logging.info(f"Sent reply: {REPLY_MESSAGE}")
    except Exception as e:
        logging.error(f"Error in auto_reply: {e}")

async def start_telethon():
    await client.start()
    logging.info("Telethon client started.")
    await client.run_until_disconnected()

def run_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telethon())

if __name__ == "__main__":
    # اجرای Telethon در یک رشته پس‌زمینه
    t = threading.Thread(target=run_telethon, daemon=True)
    t.start()

    # اجرای وب‌سرور Flask روی پورتی که Render مشخص کرده یا پیش‌فرض 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
