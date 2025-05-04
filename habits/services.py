import requests
import os

from dotenv import load_dotenv

load_dotenv()


def send_message_telegram(message, tg_chat_id):
    params = {
        "text": message,
        "chat_id": tg_chat_id,
    }
    requests.get(
        f'https://api.telegram.org/bot{os.getenv("BOT_TELEGRAM_TOKEN")}/sendMessage',
        params=params,
    )


if __name__ == "__main__":
    send_message_telegram("Привет", 1128007298)
