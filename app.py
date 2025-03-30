from flask import Flask, request, jsonify
from pyrogram import Client
import threading
import time

app = Flask(__name__)

API_ID = '20963852'
API_HASH = 'f5766ed7713132a8e3c9e7e92c2a4090'
TARGET_USERNAME = "@se36We"

app_pyrogram = Client('real_account', api_id=API_ID, api_hash=API_HASH)

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
