import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# خواندن اطلاعات حساس از Environment Variables
API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ["TELEGRAM_SESSION"]  # رشته سشن تولید شده
REPLY_MESSAGE = os.environ["TELEGRAM_REPLY_MESSAGE"]  # پیام پاسخ از سرور (بدون مقدار پیش‌فرض)

# ایجاد کلاینت تلگرام با استفاده از StringSession
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

async def main():
    await client.start()
    print("✅ کلاینت تلگرام شروع به کار کرد.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
