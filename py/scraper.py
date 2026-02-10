import os
import re
import requests
import platform
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def open_folder(path):
    path = os.path.abspath(path)
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def extract_article_number(url):
    match = re.search(r'(\d+)(?=[^\d]*$)', url)
    return match.group(1) if match else "artikel"

def run_scraper(url):
    url = url.strip()
    if not url: return

    target_class = "slick-img"
    root_img_folder = "img"
    art_num = extract_article_number(url)
    
    clean_url = url.replace('https://', '').replace('http://', '')
    site_folder_name = re.sub(r'[<>:"/\\|?*]', '-', clean_url).replace('_', '-')
    target_path = os.path.join(root_img_folder, site_folder_name)
    
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img', class_=target_class)
        
        for i, img in enumerate(img_tags):
            img_url = img.get('src') or img.get('data-lazy') or img.get('data-src')
            if not img_url: continue
            
            full_url = urljoin(url, img_url)
            try:
                img_data = requests.get(full_url, headers=headers, timeout=10).content
                parsed_path = urlparse(full_url).path
                ext = os.path.splitext(parsed_path)[1] or ".jpg"
                if "?" in ext: ext = ext.split("?")[0]

                filename = f"{art_num}{ext}" if i == 0 else f"{art_num}-{i-1}{ext}"
                save_path = os.path.join(target_path, filename)
                with open(save_path, 'wb') as f:
                    f.write(img_data)
            except: continue

        open_folder(target_path)
    except Exception as e:
        print(f"Fehler: {e}")
