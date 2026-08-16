#!/usr/bin/env bash
# Setup MetaTrader 5 + Python Windows di Linux (Ubuntu 22.04) via Wine.
# Teruji dengan wine-devel 11.15. Wine <= 11.0 gagal: "A debugger has been found".
set -euo pipefail

PREFIX="$HOME/.mt5"

# 1. WineHQ devel
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -qNP /etc/apt/sources.list.d/ "https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -cs)/winehq-$(lsb_release -cs).sources"
sudo apt-get update -qq
sudo apt-get install -y --install-recommends winehq-devel
export PATH="/opt/wine-devel/bin:$PATH"

# 2. Prefix baru (64-bit, tanpa mono/gecko)
export WINEPREFIX="$PREFIX" WINEARCH=win64 WINEDEBUG=-all
WINEDLLOVERRIDES="mscoree=d;mshtml=d" wineboot -i
wineserver -w

# 3. Installer MT5 + Python Windows
wget -nc https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
wget -nc https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
wine mt5setup.exe /auto || true
wine python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
wine "C:\\Program Files\\Python311\\python.exe" -m pip install MetaTrader5 flask

echo "Selesai. Jalankan:"
echo "  wine \"C:\\\\Program Files\\\\MetaTrader 5\\\\terminal64.exe\"   # login/akun demo"
echo "  wine \"C:\\\\Program Files\\\\Python311\\\\python.exe\" mt5_bridge.py"
echo "  BRIDGE_URL=http://localhost:5000/api/overview python3 dashboard.py"
