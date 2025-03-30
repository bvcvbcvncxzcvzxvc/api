from flask import Flask, request, jsonify
from pyrogram import Client, StringSession
import threading
import time
import os

app = Flask(__name__)

# دریافت مقادیر از متغیرهای محیطی
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')
SESSION_STRING = os.getenv('SESSION_STRING')

# استفاده از session string در صورت وجود
if SESSION_STRING:
    app_pyrogram = Client(StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
else:
    app_pyrogram = Client("real_account", api_id=API_ID, api_hash=API_HASH)

def send_license_message(license_key):
    try:
        with app_pyrogram:
            app_pyrogram.send_message(
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

    threading.Thread(target=send_license_message, args=(license_key,)).start()
    return jsonify({"status": "Verification in progress"}), 200

if __name__ == '__main__':
    app.run()
