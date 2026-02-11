import os
import json
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://anishexploits.site/anish-exploits/api.php"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        payload["parse_mode"] = parse_mode

    requests.post(url, data=payload)


def main_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }


def is_valid_phone(number):
    return number.isdigit() and len(number) == 10


def fetch_phone_data(phone):
    try:
        params = {"key": "anish", "num": phone}
        response = requests.get(API_URL, params=params, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


offset = None

print("Bot started...")

while True:
    try:
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 100, "offset": offset}
        response = requests.get(url, params=params).json()

        for update in response.get("result", []):
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if text == "/start":
                send_message(chat_id, "👋 Welcome!\nUse button below.", main_keyboard())

            elif text == "📱 Phone Lookup":
                send_message(chat_id, "📞 Send 10 digit mobile number:")

            elif is_valid_phone(text):
                send_message(chat_id, "⏳ Fetching data...")
                data = fetch_phone_data(text)
                formatted = json.dumps(data, indent=2)
                send_message(chat_id, f"<pre>{formatted}</pre>", parse_mode="HTML")

            else:
                send_message(chat_id, "❌ Invalid input. Send valid 10 digit number.")

    except Exception as e:
        print("Error:", e)

    time.sleep(1)