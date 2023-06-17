import requests
from credentials import TELEGRAM_BOT


def broadcast(text: str):
    if not TELEGRAM_BOT["token"] or not TELEGRAM_BOT["chat_id"]:
        return
    
    if not text:
        raise ValueError("text must not be empty but got empty")
    
    r = requests.post(
        url=f"https://api.telegram.org/bot{TELEGRAM_BOT['token']}/sendMessage",
        data={
            "chat_id": TELEGRAM_BOT["chat_id"],
            "parse_mode": "HTML",
            "text": f"<pre>{text}</pre>",
        },
    )

    if not r.ok:
        print(r.json())