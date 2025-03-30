from flask import Flask, request, jsonify
import time
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')
SESSION_STRING = os.getenv('SESSION_STRING')  # Session تولید شده توسط Telethon

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
else:
    client = TelegramClient("session", int(API_ID), API_HASH)

# بهتر است به جای connect() از start() استفاده کنیم تا همه چیز کامل راه بیفتد
client.start()

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
    # صرفاً جهت شبیه‌سازی تأخیر ۲ ثانیه
    time.sleep(2)

    # بدون استفاده از Thread؛ مستقیم فراخوانی می‌کنیم
    send_license_message(license_key)

    return jsonify({"status": "Verification in progress"}), 200

if __name__ == '__main__':
    app.run()
