import os
import requests

BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def notify(text: str):
    """Send a Telegram message if env vars are set; else noop."""
    if not (BOT and CHAT_ID):
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, data=payload, timeout=20)
        r.raise_for_status()
        return True
    except Exception:
        return False
