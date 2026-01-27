from dotenv import load_dotenv
import os

load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
from flask import Flask, from
import json
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "هنا_حط_توكن_صفحة_الفيسبوك"
VERIFY_TOKEN = "هنا_حط_كلمة_التحقق"

DATA_FILE = "data.json"

# دوال لحفظ وقراءة البيانات
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"players": {}, "announcement": "", "events": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# دالة لإرسال رسالة
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# Webhook للتحقق
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "خطأ"

# Webhook لتلقي الرسائل
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    for entry in data.get("entry", []):
        for message_event in entry.get("messaging", []):
            sender_id = message_event["sender"]["id"]
            if "message" in message_event:
                text = message_event["message"].get("text", "").strip()
                handle_command(sender_id, text)
    return "OK"

# دالة لمعالجة الأوامر
def handle_command(sender_id, text):
    data = load_data()
    
    if text == "مهام":
        send_message(sender_id,
            "⨳┉┅━━━━┉━━━┅┅━┅━⨳\n"
            "⌯↢  『 مهام يوميه 』\n"
            "⨳┉┅━━━━┉━━━┅┅━┅━⨳\n"
            "1- ضيف 20 عضو: مكافئة 25الف بوينت \n"
            "2- قتال معركتان رسميتان مكافئة  5الف xp\n"
            "3- قتال معركتان وديتان مكافئة 2الف xp\n"
            "4-نشر عن النظام في 5 مجموعات لا يقل اعضائها 1,000عضو مكافئة 30الف بوينت\n"
            "5-نشر عن النظام في 5 مجموعات عدد اعضائها اقل من 1,000 مكافئة 20الف بوينت \n"
            "⨳┉┅━━━━┉━━━┅┅━┅━⨳"
        )
    elif text == "ملف":
        player = data["players"].get(str(sender_id), {
            "name": "لاعب جديد",
            "level": 1,
            "warnings": 0,
            "points": 0,
            "xp": 0,
            "bag": [],
            "skills": ["تنفس السم"],
            "companion": None,
            "weapons": []
        })
        data["players"][str(sender_id)] = player
        save_data(data)
        
        send_message(sender_id,
            f"⨳┉┅━━━━┉━━━┅┅━┅━⨳\n"
            f"⌯↢  『 ملف لاعب 』\n"
            f"⨳┉┅━━━━┉━━━┅┅━┅━⨳\n"
            f"✨ اسم الشخصية: {player['name']}\n"
            f"🎖 المستوى: {player['level']}\n"
            f"⚠ الإنذارات: {player['warnings']}\n"
            f"💎 النقاط: {player['points']} Point \n"
            f"⭐ الخبرة: {player['xp']} xp\n"
            f"🎒 الحقيبة: {', '.join(player['bag']) if player['bag'] else 'فارغة'}\n"
            f"🔰 مهارات: {', '.join(player['skills'])}\n"
            f"🐺 مرافق: {player['companion'] if player['companion'] else 'لا يوجد'}\n"
            f"⚔️ أسلحة: {', '.join(player['weapons']) if player['weapons'] else 'لا يوجد'}\n"
            f"⨳┉┅━━━━┉━━━┅┅━┅━⨳"
        )
    elif text == "اعلان":
        send_message(sender_id, data.get("announcement", "لا يوجد إعلان محفوظ"))
    # ممكن تضيف بقية الأوامر بنفس الطريقة

if __name__ == "__main__":
    app.run(port=5000, debug=True)
