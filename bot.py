import os
import json
import requests
import time

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render me env variable set karna
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ===== SEND MESSAGE =====
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Send error:", e)


# ===== KEYBOARD =====
def main_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }


# ===== VALIDATION =====
def is_valid_phone(number):
    return number.isdigit() and len(number) == 10


# ===== FETCH DATA =====
def fetch_phone_data(phone):
    try:
        params = {
            "key": "7189814021",
            "num": phone
        }

        response = requests.get(API_URL, params=params, timeout=15)

        print("API RAW:", response.text)  # debug

        if not response.text.strip():
            return {"error": "Empty response from API"}

        try:
            data = response.json()
        except:
            return {
                "error": "Invalid JSON from API",
                "raw": response.text
            }

        # ===== FORCE processed_by =====
        if isinstance(data, dict):
            data["processed_by"] = "Arsu_4x"

        elif isinstance(data, list):
            data = {
                "data": data,
                "processed_by": "Arsu_4x"
            }

        return data

    except Exception as e:
        return {"error": str(e)}


# ===== MAIN LOOP =====
def main():
    offset = None
    print("Bot started...")

    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {
                "timeout": 100,
                "offset": offset
            }

            response = requests.get(url, params=params, timeout=120).json()

            for update in response.get("result", []):
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()

                # ===== START =====
                if text == "/start":
                    send_message(
                        chat_id,
                        "👋 Welcome!\nClick button below to start lookup.",
                        main_keyboard()
                    )

                # ===== BUTTON =====
                elif text == "📱 Phone Lookup":
                    send_message(chat_id, "📞 Send 10 digit mobile number:")

                # ===== PHONE INPUT =====
                elif is_valid_phone(text):
                    send_message(chat_id, "⏳ Fetching data...")

                    data = fetch_phone_data(text)

                    formatted = json.dumps(
                        data,
                        indent=2,
                        ensure_ascii=False
                    )

                    send_message(
                        chat_id,
                        f"<pre>{formatted}</pre>",
                        parse_mode="HTML"
                    )

                # ===== INVALID =====
                else:
                    send_message(chat_id, "❌ Send valid 10 digit number.")

        except Exception as e:
            print("Loop Error:", e)

        time.sleep(1)


# ===== RUN =====
if __name__ == "__main__":
    main()
