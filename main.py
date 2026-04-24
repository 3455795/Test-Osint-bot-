import os
import json
import requests
import time

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
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
        res = requests.post(url, data=payload, timeout=10).json()
        return res.get("result", {})
    except Exception as e:
        print("Send error:", e)
        return None


# ===== DELETE MESSAGE =====
def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    try:
        requests.post(url, data={
            "chat_id": chat_id,
            "message_id": message_id
        }, timeout=10)
    except Exception as e:
        print("Delete error:", e)


# ===== KEYBOARD =====
def main_keyboard():
    return {
        "keyboard": [[{"text": "📱 PHONE LOOKUP"}]],
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

        if response.status_code != 200:
            return {"error": "server"}

        if not response.text.strip():
            return {"nodata": True}

        try:
            data = response.json()
        except:
            return {"error": "server"}

        if not data or data == [] or data == {}:
            return {"nodata": True}

        final_data = {}

        if isinstance(data, list):
            final_data["data"] = data
        else:
            final_data.update(data)

        # ===== BRANDING =====
        final_data["processed_by"] = "@Arsu_4x"
        final_data["developer"] = "@OREOSELLER"
        final_data["owner_contact"] = "https://t.me/Arsu_4x"
        final_data["branding"] = "iG: @ITS_ARSU_077"

        return final_data

    except Exception as e:
        print("Fetch error:", e)
        return {"error": "server"}


# ===== MAIN LOOP =====
def main():
    offset = None
    print("🚀 Bot started...")

    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {
                "timeout": 50,
                "offset": offset
            }

            response = requests.get(url, params=params, timeout=60).json()

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
                        "🥽 <b>Main Menu</b>\n\nChoose an option below\n\n⚡ Powered by @ARSU_4X",
                        main_keyboard(),
                        parse_mode="HTML"
                    )

                # ===== BUTTON =====
                elif text == "📱 PHONE LOOKUP":
                    send_message(
                        chat_id,
                        "📱 Send 10 digit mobile number\n\n✅ Example: <code>9876543220</code>",
                        parse_mode="HTML"
                    )

                # ===== PHONE INPUT =====
                elif is_valid_phone(text):
                    msg = send_message(chat_id, "⏳ Fetching data...")
                    msg_id = msg.get("message_id") if msg else None

                    data = fetch_phone_data(text)

                    if msg_id:
                        delete_message(chat_id, msg_id)

                    if "error" in data:
                        send_message(
                            chat_id,
                            "⚠️ Server busy or API error\nTry again later."
                        )

                    elif "nodata" in data:
                        send_message(chat_id, "⚠️ No data found")

                    else:
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
                    send_message(chat_id, "❌ Invalid mobile number")

        except Exception as e:
            print("Loop crash:", e)
            time.sleep(5)  # auto-retry

        time.sleep(1)


# ===== RUN =====
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Main crash:", e)
            time.sleep(10)
