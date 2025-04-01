import os
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# خواندن اطلاعات حساس از Environment Variables (بدون مقادیر پیش‌فرض)
API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ["TELEGRAM_SESSION"]
REPLY_MESSAGE = os.environ["TELEGRAM_REPLY_MESSAGE"]

# ایجاد کلاینت Telethon با استفاده از StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage)
async def auto_reply(event):
    # جلوگیری از پاسخ به پیام‌های ارسالی توسط خودمان
    if event.out:
        return
    try:
        sender = await event.get_sender()
        sender_username = sender.username if sender else "نامشخص"
        print(f"📥 دریافت پیام از {sender_username}: {event.message.text}")
        # ارسال پاسخ خودکار
        await event.reply(REPLY_MESSAGE)
        print(f"✅ پاسخ '{REPLY_MESSAGE}' ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در auto_reply: {e}")

async def start_telethon():
    # راه‌اندازی کلاینت تلگرام و گوش دادن به پیام‌ها
    await client.start()
    print("✅ Telethon client started.")
    await client.run_until_disconnected()

def run_telethon():
    """
    اجرای Telethon در یک رشته (Thread) جداگانه.
    چون Flask روی Main Thread اجرا می‌شود، باید برای Telethon یک حلقه رویداد
    (Event Loop) جدا تعریف کنیم.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telethon())

if __name__ == "__main__":
    # اجرای Telethon در پس‌زمینه
    t = threading.Thread(target=run_telethon, daemon=True)
    t.start()

    # اجرای وب‌سرور Flask در پورت تعیین‌شده توسط Render یا 10000 به صورت پیش‌فرض
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
