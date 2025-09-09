import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

payload = {
    "chat_id": CHAT_ID,
    "text": "Test message simple"
}

response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload)
print(response.status_code, response.text)
