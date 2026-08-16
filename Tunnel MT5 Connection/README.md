# Tunnel MT5 Connection

Paket lengkap untuk menghubungkan MetaTrader 5 ke dashboard kinerja multi-bot dRBT
melalui bridge Python ("superkomputer") — baik dari PC Windows Anda sendiri (Jalur A)
maupun dari VM/VPS Linux via Wine (Jalur B).

## Isi Folder

| File | Fungsi |
|------|--------|
| `mt5_bridge.py` | Bridge read-only Flask (port 5000) — membaca akun, tick, posisi terbuka, dan histori deal dari terminal MT5, dikelompokkan per bot berdasarkan magic number |
| `dashboard.py` | Server dashboard Flask (port 8050) — mengambil data dari bridge dan menyajikan visualisasi kinerja multi-bot |
| `templates/index.html` | UI dashboard (Plotly): kurva profit kumulatif, profit bersih per bot, posisi terbuka, refresh tiap 5 detik |
| `Start_Tunnel.bat` | Skrip Windows untuk membuka tunnel Cloudflare ke bridge |
| `setup_mt5_wine.sh` | Skrip setup MT5 + Python Windows di Linux via Wine (Jalur B) |
| `ARSITEKTUR_WINDSURF_MT5_SUPERKOMPUTER.md` | Panduan arsitektur lengkap (Windsurf, MT5, superkomputer, Qwen, VPS) |

## Pemetaan Bot (Magic Number)

```
Manual                      : 0
Auto_RBT_V1_SuperSpeed      : 101 (buy) / 102 (sell)
Auto_RBT_V2_HyperSonic      : 201 (buy) / 202 (sell)
Auto_RBT_V2_HyperAgressive  : 301 (buy) / 302 (sell)
Auto_RBT_V1.1_Live (legacy) : 202604
```

## Jalur A — Bridge di PC Windows Anda (akun MT5 asli)

Syarat: terminal MT5 terinstal, terbuka, dan login di PC yang sama.

1. Salin `mt5_bridge.py` ke PC Windows Anda.
2. Install dependensi:
   ```powershell
   pip install flask MetaTrader5
   ```
3. Jalankan bridge:
   ```powershell
   python mt5_bridge.py
   ```
   Uji: buka `http://localhost:5000/api/overview` — harus tampil JSON akun Anda.
4. Buka tunnel (perlu `cloudflared.exe`, gratis):
   ```powershell
   cloudflared.exe tunnel --url http://localhost:5000
   ```
   atau klik dua kali `Start_Tunnel.bat`. Catat URL `https://....trycloudflare.com`.
5. Di mesin dashboard (VM/laptop lain):
   ```bash
   BRIDGE_URL=https://<url-tunnel>/api/overview python3 dashboard.py
   ```
6. Buka `http://localhost:8050` — dashboard tampil LIVE dengan data akun Anda.

## Jalur B — MT5 di VM/VPS Linux via Wine (sudah teruji)

Jalankan `setup_mt5_wine.sh` (atau ikuti manual di dalamnya). Ringkasan:

1. Install WineHQ **11.x devel** (wine 11.15 teruji; wine ≤11.0 gagal dengan error
   "A debugger has been found").
2. Prefix baru: `WINEPREFIX=~/.mt5 WINEARCH=win64 wineboot -i`
   dengan `WINEDLLOVERRIDES="mscoree=d;mshtml=d"`.
3. Install MT5: `wine mt5setup.exe /auto`
4. Install Python Windows 3.11 + paket:
   ```bash
   wine python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
   wine "C:\\Program Files\\Python311\\python.exe" -m pip install MetaTrader5 flask
   ```
5. Jalankan terminal: `wine "C:\\Program Files\\MetaTrader 5\\terminal64.exe"`
   — pada start pertama buka akun demo MetaQuotes-Demo (atau login akun investor Anda).
6. Jalankan bridge dengan Python Windows:
   ```bash
   cd "Tunnel MT5 Connection"
   wine "C:\\Program Files\\Python311\\python.exe" mt5_bridge.py
   ```
7. Jalankan dashboard dengan Python Linux biasa:
   ```bash
   BRIDGE_URL=http://localhost:5000/api/overview python3 dashboard.py
   ```

## Mode Demo (tanpa MT5)

```bash
DEMO=1 python3 dashboard.py
```

## Konfigurasi (environment variable)

| Variabel | Default | Keterangan |
|----------|---------|------------|
| `BRIDGE_SYMBOL` | `XAUUSD` | Simbol tick yang dipantau bridge |
| `BRIDGE_HISTORY_DAYS` | `30` | Jendela histori deal (hari) |
| `BRIDGE_URL` | `http://localhost:5000/api/overview` | Alamat bridge untuk dashboard |
| `DEMO` | `0` | `1` = dashboard pakai data simulasi |

## Keamanan (WAJIB)

- Bridge ini **read-only** — tidak ada endpoint kirim/tutup order. Jangan tambahkan.
- Gunakan **investor password** (read-only) untuk visualisasi, bukan password utama.
- Jangan biarkan URL tunnel tersebar; matikan tunnel jika tidak dipakai.
- Jangan commit API key/token ke repo. Rotate semua key yang pernah terkirim di chat
  (Qwen, ngrok, GitHub, dll).
- Live trading bot tetap nonaktif secara default (`AUTO_RBT_LIVE_TRADING=0`).
