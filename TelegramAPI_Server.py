import os
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# مسیر جدید برای ارسال تنظیمات به سمت مشتری
@app.route('/config')
def get_config():
    # دو متغیر محیطی که می‌خواهید به مشتری بروند
    telegram_username = os.environ["TELEGRAM_USERNAME"]
    telegram_initial_message = os.environ["TELEGRAM_INITIAL_MESSAGE"]
    
    # می‌توانید در صورت نیاز، احراز هویت انجام دهید یا رمزگذاری کنید
    # اما اینجا ساده‌ترین حالت را در نظر می‌گیریم.
    
    return jsonify({
        "TELEGRAM_USERNAME": telegram_username,
        "TELEGRAM_INITIAL_MESSAGE": telegram_initial_message
    })

# --- تنظیمات Telethon برای پاسخ خودکار ---
API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ["TELEGRAM_SESSION"]
REPLY_MESSAGE = os.environ["TELEGRAM_REPLY_MESSAGE"]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage)
async def auto_reply(event):
    if event.out:
        return
    try:
        sender = await event.get_sender()
        sender_username = sender.username if sender else "نامشخص"
        print(f"📥 دریافت پیام از {sender_username}: {event.message.text}")
        await event.reply(REPLY_MESSAGE)
        print(f"✅ پاسخ '{REPLY_MESSAGE}' ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در auto_reply: {e}")

async def start_telethon():
    await client.start()
    print("✅ Telethon client started.")
    await client.run_until_disconnected()

def run_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telethon())

if __name__ == "__main__":
    # اجرای Telethon در پس‌زمینه
    t = threading.Thread(target=run_telethon, daemon=True)
    t.start()

    # اجرای وب‌سرور Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
