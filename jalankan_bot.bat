@echo off
title Bot Loker Sukabumi (Autopilot)
echo Menjalankan Bot Loker Sukabumi Otomatis...
cd /d "C:\Users\subaa\.gemini\antigravity-ide\scratch\loker-scraper"
python main.py
echo Proses selesai! Jendela akan tertutup otomatis...
timeout /t 5 >nul
