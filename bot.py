import os
import json
import requests
import time

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ===== SEND MESSAGE (RETURN MESSAGE ID) =====
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
        return res.get("result", {}).get("message_id")
    except Exception as e:
        print("Send error:", e)
        return None


# ===== DELETE MESSAGE =====
def delete_message(chat_id, message_id):
    try:
        url = f"{BASE_URL}/deleteMessage"
        requests.post(url, data={
            "chat_id": chat_id,
            "message_id": message_id
        }, timeout=10)
    except Exception as e:
        print("Delete error:", e)


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
        params = {"key": "7189814021", "num": phone}
        response = requests.get(API_URL, params=params, timeout=15)

        if response.status_code != 200:
            return {"error": "server"}

        if not response.text.strip():
            return {"error": "no_data"}

        try:
            data = response.json()
        except:
            return {"error": "server"}

        if data == []:
            return {"error": "no_data"}

        final_data = {}

        if isinstance(data, list):
            final_data["data"] = data
        else:
            final_data.update(data)

        # ===== BRANDING =====
        final_data["processed_by"] = "@Arsu_4x"
        final_data["developer"] = "@OREOSELLER"
        final_data["owner_contact"] = "https://t.me/Arsu_4x"
        final_data["branding"] = "@ARSU_4X"

        return final_data

    except Exception as e:
        print("API Error:", e)
        return {"error": "server"}


# ===== MAIN LOOP =====
def main():
    offset = None
    print("Bot started...")

    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {"timeout": 100, "offset": offset}

            response = requests.get(url, params=params, timeout=120).json()

            for update in response.get("result", []):
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()

                # ===== START =====
                if text.startswith("/start"):
                    send_message(
                        chat_id,
                        "⚡ Main Menu\nChoose an option below\n⚡ Powered by @ARSU_4X",
                        main_keyboard(),
                        parse_mode="Markdown"
                    )

                # ===== BUTTON =====
                elif text == "📱 Phone Lookup":
                    send_message(
                        chat_id,
                        "📱 *Send 10 digit mobile number*\n\n✅ Example: `9876543220`",
                        parse_mode="Markdown"
                    )

                # ===== PHONE INPUT =====
                elif is_valid_phone(text):

                    loading_msg_id = send_message(chat_id, "⏳ Fetching data...")

                    data = fetch_phone_data(text)

                    # 🧹 delete loading
                    if loading_msg_id:
                        delete_message(chat_id, loading_msg_id)

                    # ❌ no data
                    if data.get("error") == "no_data":
                        send_message(chat_id, "⚠️ No data found")
                        continue

                    # ❌ server error
                    if data.get("error") == "server":
                        send_message(
                            chat_id,
                            "⚠️ Server busy or API unreachable\nPlease try again later."
                        )
                        continue

                    # ✅ success JSON
                    formatted = json.dumps(data, indent=2, ensure_ascii=False)

                    send_message(
                        chat_id,
                        f"<pre>{formatted}</pre>",
                        parse_mode="HTML"
                    )

                # ===== INVALID =====
                else:
                    send_message(chat_id, "❌ Invalid mobile number")

        except Exception as e:
            print("Loop Error:", e)

        time.sleep(1)


# ===== RUN =====
if __name__ == "__main__":
    main()
