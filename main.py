# main.py
import requests
from bs4 import BeautifulSoup
import time
import os

# -------- CONFIG --------
# Liste de recherches à surveiller avec filtre de prix
SEARCH_LIST = [
    {"url": "https://www.vinted.fr/vetements?search_text=lacoste+zip+noir&price_to=50", "name": "Lacoste zip noir"},
    {"url": "https://www.vinted.fr/vetements?search_text=nike+sweat&price_to=50", "name": "Nike sweat"},
    {"url": "https://www.vinted.fr/vetements?search_text=levi%27s+jean&price_to=60", "name": "Levi's jean"}
]
CHECK_INTERVAL = 120  # en secondes (2 min)

# Telegram (variables secrètes dans Replit ou .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------- FONCTIONS --------
def send_telegram_message(title, photo_url, ad_url):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Voir l'annonce", "url": ad_url}]
        ]
    }

    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": title,
        "reply_markup": str(keyboard).replace("'", '"')
    }

    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)
    except Exception as e:
        print("Erreur en envoyant le message Telegram:", e)

def check_vinted(search_url):
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all("div", class_="feed-grid__item")
    new_ads = []
    for item in items:
        link_tag = item.find("a")
        if link_tag:
            link = link_tag["href"]
            title = item.get_text(strip=True)
            url = "https://www.vinted.fr" + link
            new_ads.append((title, url))
    return new_ads

# -------- MAIN LOOP --------
if __name__ == "__main__":
    seen_ads = set()

    while True:
        try:
            for search in SEARCH_LIST:
                ads = check_vinted(search['url'])
                for title, url in ads:
                    if url not in seen_ads:
                        seen_ads.add(url)
                        message = f"🔥 Nouvelle annonce ({search['name']}):\n{title}\n{url}"
                        print(message)
                        send_telegram_message(message)
        except Exception as e:
            print("Erreur lors de la veille Vinted :", e)

        time.sleep(CHECK_INTERVAL)
