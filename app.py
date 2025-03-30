from flask import Flask, request, jsonify
import time
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)


API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TARGET_USER = os.getenv('TARGET_USERNAME')  
SESSION_STRING = os.getenv('SESSION_STRING')  


if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("session", API_ID, API_HASH)

client.start()  

def send_license_message(license_key):
    try:
    
        if TARGET_USER.isdigit():
            client.send_message(int(TARGET_USER), f"🚨 New License Request!\n\nLicense Key: {license_key}\nStatus: Verifying...")
        else:
            client.send_message(TARGET_USER, f"🚨 New License Request!\n\nLicense Key: {license_key}\nStatus: Verifying...")

        print("✅ Message sent successfully.")
    except Exception as e:
        print("❌ Error sending message:", e)

@app.route('/verify_license', methods=['POST'])
def verify_license():
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({"error": "Invalid request, missing license_key"}), 400

    license_key = data['license_key']
    time.sleep(2) 
    send_license_message(license_key)
    return jsonify({"status": "Verification in progress"}), 200

if __name__ == '__main__':
    app.run()
