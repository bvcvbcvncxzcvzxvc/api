from flask import Flask, request, jsonify
import threading
import time
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

# دریافت مقادیر از متغیرهای محیطی
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')
SESSION_STRING = os.getenv('SESSION_STRING')  # رشته session تولید شده توسط Telethon

# توجه: API_ID باید عددی (int) باشد
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
else:
    client = TelegramClient("session", int(API_ID), API_HASH)

# اتصال به تلگرام (در حالت همزمان)
client.connect()

def send_license_message(license_key):
    try:
        client.send_message(
            TARGET_USERNAME,
            f"🚨 New License Request!\n\nLicense Key: {license_key}\nStatus: Verifying..."
        )
    except Exception as e:
        print("❌ Error sending message:", e)

@app.route('/verify_license', methods=['POST'])
def verify_license():
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({"error": "Invalid request, missing license_key"}), 400

    license_key = data['license_key']
    time.sleep(2)

    # اجرای ارسال پیام در یک ترد جداگانه
    threading.Thread(target=send_license_message, args=(license_key,)).start()
    return jsonify({"status": "Verification in progress"}), 200

if __name__ == '__main__':
    app.run()
