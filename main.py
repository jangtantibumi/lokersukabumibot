import time
import random
from scrapers.lokersmi_scraper import get_jobs_from_lokersmi, scrape_job_details
from ai_processor import process_job_with_ai
from blogger_api import create_post, get_previous_post
from db_manager import init_db, is_posted, mark_as_posted

THUMBNAILS = [
    "https://res.cloudinary.com/ds6pqyquq/image/upload/v1782899298/BANNER_LOKERSUKABUMIMYID_1_icqkku.webp",
    "https://res.cloudinary.com/ds6pqyquq/image/upload/v1782899298/BANNER_LOKERSUKABUMIMYID_2_dgevwf.webp",
    "https://res.cloudinary.com/ds6pqyquq/image/upload/v1782899298/BANNER_LOKERSUKABUMIMYID_4_nhlpjh.webp",
    "https://res.cloudinary.com/ds6pqyquq/image/upload/v1782899299/BANNER_LOKERSUKABUMIMYID_3_kkvkti.webp",
    "https://res.cloudinary.com/ds6pqyquq/image/upload/v1782899300/BANNER_LOKERSUKABUMIMYID_5-1_awbjod.webp"
]

def main():
    print("Memulai Bot Loker Sukabumi...")
    init_db()
    
    # 1. Scrape URL loker terbaru
    job_urls = get_jobs_from_lokersmi()
    print(f"Ditemukan {len(job_urls)} loker di halaman utama.")
    
    for url in job_urls:
        if is_posted(url):
            print(f"Melewati (Sudah diposting): {url}")
            continue
            
        print(f"Memproses loker baru: {url}")
        
        # 2. Ambil detail loker (termasuk dekripsi Cloudflare email)
        job_detail = scrape_job_details(url)
        if not job_detail:
            continue
            
        # 3. Proses dengan AI
        print("Menulis ulang dengan Gemini AI...")
        ai_result = process_job_with_ai(job_detail['title'], job_detail['description'])
        
        if not ai_result:
            print("Gagal memproses dengan AI. Melewati loker ini.")
            continue
            
        # 4. Susun Format Judul dan Konten
        daerah = ai_result.get('daerah', 'Sukabumi')
        posisi = ai_result.get('posisi', '')
        pendidikan = ai_result.get('pendidikan', '')
        perusahaan = ai_result.get('perusahaan', '')
        
        # Filter kata 'tidak disebutkan' dll
        def clean_title_part(part):
            if not part: return ""
            lower = part.lower()
            if "tidak" in lower or "unknown" in lower or "spesifik" in lower or "informasi" in lower or "tersedia" in lower:
                return ""
            return part
            
        daerah_clean = clean_title_part(daerah) or "Sukabumi"
        posisi_clean = clean_title_part(posisi)
        per_clean = clean_title_part(perusahaan)
        pendidikan_clean = clean_title_part(pendidikan)
        
        # Format judul dinamis baru
        new_title = f"Loker {daerah_clean.title()} {posisi_clean} {per_clean}".strip()
        new_title = " ".join(new_title.split()) # Hapus spasi ganda
        
        # Pilih thumbnail acak
        thumbnail_url = random.choice(THUMBNAILS)
        thumbnail_html = f'<div style="text-align: center;"><img src="{thumbnail_url}" alt="{new_title}" style="max-width: 100%; height: auto;" /></div><br/>'
        
        # Ambil Previous Post
        prev_post = get_previous_post()
        if prev_post:
            related_html = f"<br/><hr/><p>Loker sebelumnya: <a href='{prev_post['url']}'>{prev_post['title']}</a></p>"
        else:
            related_html = f"<br/><hr/><p>Loker sebelumnya: <a href='https://lokersukabumi.my.id/'>Kunjungi Halaman Depan</a></p>"
        
        # Tambahan Doa Penutup
        doa_html = "<br/><p style='text-align:center;'><em>Semoga Anda yang berniat baik dan berjuang untuk mencari nafkah yang hallal selalu sehat dan sukses.</em></p>"
        
        # Gabungkan semua konten
        final_content = thumbnail_html + ai_result.get('content_html', '') + related_html + doa_html
        
        # Kumpulkan Label sesuai urutan: Posisi, Pendidikan, Daerah
        raw_labels = [posisi_clean, pendidikan_clean, daerah_clean]
        labels = [l.strip() for l in raw_labels if l and l.strip()]
        
        # 5. Posting ke Blogger
        # is_draft=False agar langsung tayang (live)
        print(f"Memposting: {new_title}")
        success = create_post(new_title, final_content, labels=labels, is_draft=False)
        
        if success:
            mark_as_posted(url)
            print(f"Sukses! Menunggu 15 detik untuk menghindari rate limit Google...")
            time.sleep(15)
        else:
            print("Gagal memposting ke Blogger.")
            
    print("Selesai!")

if __name__ == '__main__':
    main()
