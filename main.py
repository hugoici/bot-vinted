import requests
from bs4 import BeautifulSoup
import time
import os
import json

# -------- CONFIG --------
SEARCH_LIST = [
    {"url": "https://www.vinted.fr/vetements?search_text=lacoste+zip+noir&price_to=50", "name": "Lacoste zip noir"},
    {"url": "https://www.vinted.fr/vetements?search_text=nike+sweat&price_to=50", "name": "Nike sweat"},
    {"url": "https://www.vinted.fr/vetements?search_text=levi%27s+jean&price_to=60", "name": "Levi's jean"}
]
CHECK_INTERVAL = 300  # en secondes (5 min)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------- FONCTIONS --------
def send_telegram_message(title, photo_url, ad_url):
    keyboard = {"inline_keyboard": [[{"text": "Voir l'annonce", "url": ad_url}]]}
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": title,
        "reply_markup": json.dumps(keyboard)
    }
    try:
        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)
        print(f"Telegram response: {response.status_code}, {response.text}")
    except Exception as e:
        print("Erreur en envoyant le message Telegram:", e)

def check_vinted(search_url):
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", class_="feed-grid__item")
    new_ads = []
    for item in items:
        link_tag = item.find("a")
        img_tag = item.find("img")
        if link_tag and img_tag:
            href = link_tag.get("href", "")
            if href.startswith("http"):
                url = href
            else:
                url = "https://www.vinted.fr" + href

            # Récupérer titre, état et prix
            title_raw = item.get_text(strip=True)

            # Supprimer "Enlevé"
            title_raw = title_raw.replace("Enlevé", "")

            parts = title_raw.split('·')
            if len(parts) >= 2:
                clothing_name = parts[0].strip()
                state = parts[1].strip()

                # Extraire prix initial uniquement
                price_part = clothing_name.split()
                price = price_part[0] if price_part else ''

                # Format final : nom, saut de ligne, état, saut de ligne, espace, prix + like ❤️
                title = f"🔥 Nouvelle annonce : {clothing_name}\n\n{state}\n\n{price} € , like ❤️"

            photo_url = img_tag.get("src", "")
            if photo_url.startswith("//"):
                photo_url = "https:" + photo_url

            if url and photo_url:
                new_ads.append((title, photo_url, url))
    return new_ads

# -------- MAIN LOOP --------
if __name__ == "__main__":
    seen_ads = set()
    while True:
        try:
            for search in SEARCH_LIST:
                ads = check_vinted(search['url'])
                print(f"Recherche: {search['name']}, {len(ads)} annonces trouvées")
                for title, photo_url, url in ads:
                    if url not in seen_ads:
                        seen_ads.add(url)
                        print(f"Envoi de l'annonce: {title}")
                        print(f"Photo: {photo_url}")
                        print(f"URL: {url}")
                        send_telegram_message(title, photo_url, url)
        except Exception as e:
            print("Erreur lors de la veille Vinted :", e)
        time.sleep(CHECK_INTERVAL)
