from dotenv import load_dotenv
import os
from flask import Flask, request
import json
import requests

# =========================
# تحميل متغيرات البيئة
# =========================
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

if not PAGE_ACCESS_TOKEN or not VERIFY_TOKEN:
    raise ValueError("❌ PAGE_ACCESS_TOKEN أو VERIFY_TOKEN غير موجودين في .env")

# =========================
# إعداد التطبيق
# =========================
app = Flask(__name__)
DATA_FILE = "data.json"

# =========================
# أدوات مساعدة
# =========================
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "players": {},
            "announcement": "",
            "tasks": ""
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v16.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, params=params, json=payload)

# =========================
# Webhook
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "❌ فشل التحقق", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            if "message" in event and "text" in event["message"]:
                text = event["message"]["text"].strip()
                handle_command(sender_id, text)
    return "OK", 200

# =========================
# الأوامر
# =========================
def handle_command(sender_id, text):
    data = load_data()

    # --- مهام ---
    if text == "مهام":
        send_message(sender_id, data["tasks"] or "لا توجد مهام حاليًا")

    # --- إعلان ---
    elif text == "اعلان":
        send_message(sender_id, data["announcement"] or "لا يوجد إعلان")

    # --- ملف اللاعب ---
    elif text == "ملف":
        player = data["players"].get(str(sender_id))
        if not player:
            player = {"level": 1, "points": 0, "xp": 0, "warnings": 0}
            data["players"][str(sender_id)] = player
            save_data(data)
        send_message(
            sender_id,
            f"🎖 المستوى: {player['level']}\n"
            f"💎 النقاط: {player['points']}\n"
            f"⭐ الخبرة: {player['xp']}\n"
            f"⚠ التحذيرات: {player['warnings']}"
        )

    # --- أمر غير معروف ---
    else:
        send_message(sender_id, "❓ أمر غير معروف")

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
