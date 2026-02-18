import os
import re
import requests
import platform
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def open_folder(path):
    """Öffnet den Ordner unabhängig vom Terminal-Prozess."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return

    try:
        if platform.system() == "Windows":
            # creationflags=0x00000008 (DETACHED_PROCESS) erlaubt das Öffnen aus Threads
            subprocess.Popen(['explorer', path], creationflags=0x00000008)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Fehler beim Öffnen des Explorers: {e}")

def extract_article_number(url):
    """Extrahiert die Artikelnummer (letzte Zahlenfolge) aus der URL."""
    match = re.search(r'(\d+)(?=[^\d]*$)', url)
    return match.group(1) if match else "artikel"

def run_scraper(url_input):
    url_input = url_input.strip()
    if not url_input: 
        return

    # URL Logik: Wenn nur eine Nummer eingegeben wurde, die Suche nutzen
    if url_input.isdigit():
        url = f"https://shop.api.de/product/details/{url_input}"
    else:
        url = url_input

    root_img_folder = "img"
    art_num = extract_article_number(url)
    
    # Ordnernamen generieren und säubern
    clean_url = url.split('/')[-1].split('?')[0]
    site_folder_name = re.sub(r'[<>:"/\\|?*]', '-', clean_url)
    target_path = os.path.join(os.getcwd(), root_img_folder)
    
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    # Realistischer Header, um Blockaden zu vermeiden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    try:
        # allow_redirects ist wichtig für die Artikelsuche
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suche nach Bildern (erweiterte Klassen-Suche)
        img_tags = soup.find_all('img', class_=re.compile(r'slick-img|product|detail|main-img'))
        
        count = 0
        for img in img_tags:
            # Lazy-Loading Attribute prüfen
            img_url = img.get('data-lazy') or img.get('data-src') or img.get('src') or img.get('data-flickity-lazyload')
            if not img_url or "base64" in img_url: 
                continue
            
            full_url = urljoin(url, img_url)
            
            try:
                img_res = requests.get(full_url, headers=headers, timeout=10)
                img_data = img_res.content
                
                # Dateiendung extrahieren
                parsed_path = urlparse(full_url).path
                ext = os.path.splitext(parsed_path)[1] or ".jpg"
                if "?" in ext: 
                    ext = ext.split("?")[0]

                # BENENNUNGSLOGIK:
                # 1. Bild: Artikelnummer.jpg
                # 2. Bild: Artikelnummer-0.jpg
                # 3. Bild: Artikelnummer-1.jpg
                if count == 0:
                    filename = f"{art_num}{ext}"
                else:
                    filename = f"{art_num}-{count-1}{ext}"

                save_path = os.path.join(target_path, filename)
                with open(save_path, 'wb') as f:
                    f.write(img_data)
                
                count += 1
            except Exception:
                continue

        # Explorer nur öffnen, wenn Bilder gefunden wurden

    except Exception as e:
        print(f"Scraper-Fehler: {e}")
