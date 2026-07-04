import requests
from bs4 import BeautifulSoup
import re

def decode_cf_email(cfemail):
    if not cfemail:
        return ""
    r = int(cfemail[:2], 16)
    email = "".join([chr(int(cfemail[i:i+2], 16) ^ r) for i in range(2, len(cfemail), 2)])
    return email

def get_jobs_from_lokersmi():
    base_url = "https://lokersmi.co.id/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal mengambil halaman utama: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    
    # Menemukan semua link loker di halaman depan
    # Disesuaikan secara umum dengan struktur lokersmi.co.id
    for article in soup.find_all('article'):
        title_tag = article.find('h2') or article.find('h3')
        if not title_tag:
            continue
            
        a_tag = title_tag.find('a')
        if not a_tag:
            continue
            
        url = a_tag.get('href')
        if not url:
            continue
            
        jobs.append(url)
        
    return jobs

def scrape_job_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal mengambil detail loker dari {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ambil judul asli
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    # Ambil deskripsi utama (content)
    content_div = soup.find('div', class_=re.compile(r'entry-content|content|post-content'))
    
    # Dekripsi Cloudflare Email jika ada
    if content_div:
        for cf_span in content_div.find_all('span', class_='__cf_email__'):
            cfemail = cf_span.get('data-cfemail')
            if cfemail:
                decoded_email = decode_cf_email(cfemail)
                cf_span.replace_with(f"{decoded_email}")
        for cf_a in content_div.find_all('a', class_='__cf_email__'):
            cfemail = cf_a.get('data-cfemail')
            if cfemail:
                decoded_email = decode_cf_email(cfemail)
                cf_a.replace_with(f"{decoded_email}")

    description = content_div.get_text(separator='\n', strip=True) if content_div else ""
    
    # Ekstrak Info Lamar (dari popup modal)
    apply_div = soup.find('div', class_='apply-job') or soup.find(id='apply-content')
    if apply_div:
        # Buang footer yang berisi logo/info tdk penting
        footer_apply = apply_div.find('div', class_='footer-apply')
        if footer_apply:
            footer_apply.decompose()
            
        # Dekripsi email CF di dalam apply_div
        for cf_span in apply_div.find_all('span', class_='__cf_email__'):
            cfemail = cf_span.get('data-cfemail')
            if cfemail:
                decoded_email = decode_cf_email(cfemail)
                cf_span.replace_with(f"{decoded_email}")
        for cf_a in apply_div.find_all('a', class_='__cf_email__'):
            cfemail = cf_a.get('data-cfemail')
            if cfemail:
                decoded_email = decode_cf_email(cfemail)
                cf_a.replace_with(f"{decoded_email}")
                
        apply_text = apply_div.get_text(separator='\n', strip=True)
        if apply_text:
            description += "\n\nINFORMASI CARA MELAMAR:\n" + apply_text
    
    return {
        'url': url,
        'title': title,
        'description': description
    }
