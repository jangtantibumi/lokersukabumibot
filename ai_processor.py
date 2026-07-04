import os
import json
from google import genai
from google.genai import types

def get_api_key():
    try:
        with open("gemini_api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def process_job_with_ai(title, description):
    api_key = get_api_key()
    if not api_key:
        print("API Key Gemini tidak ditemukan di gemini_api_key.txt")
        return None

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
Tugas Anda adalah menulis ulang informasi lowongan kerja berikut menjadi postingan blog yang menarik.
Ikuti instruksi berikut dengan ketat:
1. Parafrase teks secara total agar kalimatnya berbeda sama sekali dengan sumber aslinya. Gunakan copywriting yang menarik, profesional, rapi, dan WAJIB mematuhi kaidah tata bahasa Indonesia (PUEBI/EYD) yang baik dan benar (gunakan HTML tags seperti <p>, <ul>, <li>, <strong>, <br> jika perlu).
2. SANGAT PENTING: Kriteria lowongan, syarat, atau kualifikasi WAJIB MUTLAK ditulis dalam bentuk list (daftar peluru) menggunakan tag HTML <ul> dan <li>.
3. Hapus semua nama situs sumber atau link sumber aslinya (seperti lokersmi.co.id atau sejenisnya).
4. SANGAT PENTING: Paragraf pertama WAJIB diawali persis dengan kode HTML berikut (termasuk tanda strip yang menyatu di dalam area transparan):
`<strong style='color: green;'>lokersukabumi.my.id</strong><span style='color: transparent; font-size: 1pt;'> - loker sukabumi</span> `
Langsung lanjutkan kalimat pertama artikel setelah kode tersebut di baris yang sama.
5. SANGAT PENTING (SPASI): JANGAN gunakan tag `<br><br>` ganda atau membuat paragraf kosong. Pastikan antar paragraf dan list (<ul>) hanya memiliki jarak 1 spasi (single spacing) agar terlihat rapi dan padat di layar HP. Hindari penggunaan tag `<p>` berlebih, cukup gunakan `<br>` tunggal jika ingin pindah baris biasa.
6. Tempatkan bagian "INFORMASI CARA MELAMAR" tepat setelah paragraf terakhir keterangan loker. WAJIB bungkus seluruh bagian "Cara Melamar" tersebut ke dalam tag <blockquote> agar tampil sebagai block note yang rapi.
7. Pada kalimat penutup (paling bawah di dalam content_html), wajib ada kata 'loker sukabumi' yang dijadikan anchor link persis seperti ini: <a href="https://lokersukabumi.my.id">loker sukabumi</a>.
8. Identifikasi Nama Perusahaan, Posisi, Daerah penempatan, dan Tingkat Pendidikan dari lowongan tersebut.
9. Jika daerah penempatannya di wilayah Sukabumi (Kota/Kabupaten), sebutkan "Sukabumi" pada bagian daerah. Jika jelas tertulis di luar Sukabumi, tuliskan nama daerah aslinya tersebut.
10. Kembalikan data murni dalam format JSON persis dengan struktur berikut:
{{
    "perusahaan": "...",
    "posisi": "...",
    "daerah": "...",
    "pendidikan": "...",
    "content_html": "..."
}}

Berikut adalah data lowongan kerjanya:
Judul Asli: {title}
Deskripsi:
{description}
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Error memproses dengan Gemini: {e}")
        return None
