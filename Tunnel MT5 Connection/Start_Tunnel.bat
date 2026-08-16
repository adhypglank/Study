@echo off
REM Buka tunnel Cloudflare ke bridge MT5 (port 5000).
REM Unduh cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
REM Jalankan mt5_bridge.py dulu, lalu jalankan file ini.
cloudflared.exe tunnel --url http://localhost:5000
pause
