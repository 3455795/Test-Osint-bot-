import os
import json
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/"


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
        res = requests.post(url, data=payload, timeout=10)
        print("SEND:", res.text)
        return res.json().get("result", {}).get("message_id")
    except Exception as e:
        print("Send error:", e)
        return None


# ===== DELETE MESSAGE =====
def delete_message(chat_id, message_id):
    try:
        requests.post(f"{BASE_URL}/deleteMessage", data={
            "chat_id": chat_id,
            "message_id": message_id
        })
    except:
        pass


# ===== KEYBOARD (FIXED FORMAT) =====
def main_keyboard():
    return {
        "keyboard": [
            [{"text": "📱 Phone Lookup"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# ===== VALIDATION =====
def is_valid_phone(num):
    return num.isdigit() and len(num) == 10


# ===== FETCH DATA =====
def fetch_data(phone):
    try:
        r = requests.get(API_URL, params={
            "key": "7189814021",
            "num": phone
        }, timeout=15)

        if r.status_code != 200:
            return {"error": "server"}

        if not r.text.strip():
            return {"error": "no_data"}

        try:
            data = r.json()
        except:
            return {"error": "server"}

        if data == []:
            return {"error": "no_data"}

        final = {}

        if isinstance(data, list):
            final["data"] = data
        else:
            final.update(data)

        # branding
        final["processed_by"] = "@Arsu_4x"
        final["developer"] = "@OREOSELLER"
        final["owner_contact"] = "https://t.me/Arsu_4x"
        final["branding"] = "@ARSU_4X"

        return final

    except Exception as e:
        print("API error:", e)
        return {"error": "server"}


# ===== MAIN LOOP =====
def main():
    offset = None
    print("Bot running...")

    while True:
        try:
            res = requests.get(f"{BASE_URL}/getUpdates", params={
                "timeout": 100,
                "offset": offset
            }).json()

            for upd in res.get("result", []):
                offset = upd["update_id"] + 1

                msg = upd.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                text_clean = text.lower().strip()

                print("RECV:", text_clean)

                # ===== START FIX (IMPORTANT) =====
                if text_clean.startswith("/start"):
                    send_message(
                        chat_id,
                        "⚡ *Main Menu*\n\nChoose an option below\n\n⚡ Powered by @ARSU_4X",
                        reply_markup=main_keyboard(),
                        parse_mode="Markdown"
                    )
                    continue

                # ===== BUTTON =====
                if text == "📱 Phone Lookup":
                    send_message(
                        chat_id,
                        "📱 *Send 10 digit mobile number*\n\n✅ Example: `9876543220`",
                        parse_mode="Markdown"
                    )
                    continue

                # ===== NUMBER =====
                if is_valid_phone(text):
                    loading_id = send_message(chat_id, "⏳ Fetching data...")

                    data = fetch_data(text)

                    if loading_id:
                        delete_message(chat_id, loading_id)

                    if data.get("error") == "no_data":
                        send_message(chat_id, "⚠️ No data found")
                        continue

                    if data.get("error") == "server":
                        send_message(chat_id, "⚠️ Server busy or API unreachable\nPlease try again later.")
                        continue

                    formatted = json.dumps(data, indent=2, ensure_ascii=False)

                    send_message(chat_id, f"<pre>{formatted}</pre>", parse_mode="HTML")
                    continue

                # ===== INVALID =====
                if text:
                    send_message(chat_id, "❌ Invalid mobile number")

        except Exception as e:
            print("Loop error:", e)

        time.sleep(1)


if __name__ == "__main__":
    main()
