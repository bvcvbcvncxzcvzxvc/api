from flask import Flask, request, jsonify
import time
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

# دریافت مقادیر از متغیرهای محیطی
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')  # مثلا "@se36We"
SESSION_STRING = os.getenv('SESSION_STRING')    # رشته session تولید شده توسط Telethon

# ایجاد کلاینت تلگرام
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("session", API_ID, API_HASH)

client.start()  # اتصال و استارت کلاینت

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
    time.sleep(2)  # شبیه‌سازی تأخیر
    send_license_message(license_key)
    return jsonify({"status": "Verification in progress"}), 200

if __name__ == '__main__':
    app.run()
