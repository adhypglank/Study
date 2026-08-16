# Panduan: Windsurf → MetaTrader 5 → Superkomputer.py → VPS Awan (QwenCloud)

Catatan kejujuran teknis di depan:
- Library resmi `MetaTrader5` (PyPI) **hanya berjalan di Windows** dan membutuhkan terminal MT5 yang sedang berjalan di mesin yang sama. Di Linux hanya bisa lewat Wine (tidak resmi) atau lewat jembatan socket ke mesin Windows.
- "QwenCloud" bukan nama produk cloud resmi yang saya bisa verifikasi. Qwen adalah model LLM Alibaba (diakses via DashScope/Alibaba Cloud Model Studio), sedangkan VPS-nya adalah **Alibaba Cloud ECS**. Jadi arsitektur realistis: **ECS (Windows) sebagai VPS** + **Qwen API sebagai "otak" AI**. Kalau yang Anda maksud layanan lain, kirim link-nya dan saya sesuaikan.

---

## Tahap 0 — Arsitektur target

```
Windsurf (laptop Anda)            VPS Windows (Alibaba Cloud ECS)
+------------------+   SSH/RDP   +--------------------------------+
| editor + Cascade | ----------> | MetaTrader5 terminal (login)   |
| deploy & debug   |   remote    | Superkomputer.py (strategi)    |
+------------------+             | bridge/API (FastAPI, port 8000)|
                                 +--------------------------------+
                                        |  HTTPS
                                        v
                                 Qwen API (DashScope) — analisis/keputusan AI
```

Kunci: MT5 dan `Superkomputer.py` **satu mesin** (Windows). Windsurf hanya alat kerja/remote, bukan jalur eksekusi order.

---

## Tahap 1 — Siapkan MT5 lokal dulu (validasi konsep)

1. Install MT5 (dari broker Anda), login akun **demo** terlebih dahulu.
2. Tools → Options → Expert Advisors → centang *Allow Algo Trading*.
3. Install Python 3.11 (64-bit) lalu:
   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   pip install MetaTrader5 pandas numpy python-dotenv fastapi uvicorn
   ```
4. Uji koneksi:
   ```python
   import MetaTrader5 as mt5, os
   assert mt5.initialize(
       login=int(os.environ["MT5_LOGIN"]),
       password=os.environ["MT5_PASSWORD"],
       server=os.environ["MT5_SERVER"],
   ), mt5.last_error()
   print(mt5.account_info()._asdict())
   print(mt5.symbol_info_tick("XAUUSD"))
   mt5.shutdown()
   ```
   Kredensial lewat variabel lingkungan / `.env` (jangan pernah di-commit).

---

## Tahap 2 — Bentuk `Superkomputer.py` jadi modul yang bisa diuji

Pisahkan tiga lapis supaya bisa di-unit-test tanpa MT5 nyala:

- `broker.py` — semua panggilan `mt5.*` (ambil harga, kirim/tutup order).
- `strategy.py` — fungsi murni: input DataFrame harga → output sinyal (`BUY/SELL/HOLD`, SL, TP, lot). Tanpa I/O.
- `risk.py` — batas lot, max drawdown, max posisi, jam trading.
- `Superkomputer.py` — orkestrator: loop baca harga → strategy → risk → broker.

Contoh kirim order (selalu lewat `risk.py` dulu):
```python
req = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol, "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick(symbol).ask,
    "sl": sl, "tp": tp,
    "deviation": 20, "magic": 202601,
    "type_filling": mt5.ORDER_FILLING_IOC,
}
res = mt5.order_send(req)
if res.retcode != mt5.TRADE_RETCODE_DONE:
    log.error("order gagal: %s", res)
```

---

## Tahap 3 — Sambungkan Windsurf secara "otomatis"

Yang otomatis di Windsurf ada tiga bentuk, pilih sesuai kebutuhan:

1. **Remote development** — Windsurf → *Remote - SSH* ke VPS, buka folder proyek di VPS, edit & jalankan langsung di sana. Ini cara paling praktis.
2. **Task/launch config** — simpan `.vscode/tasks.json` di repo agar satu klik menjalankan `uvicorn bridge:app` atau `python Superkomputer.py`.
3. **MCP server** — supaya Cascade (AI Windsurf) bisa memanggil MT5 Anda sebagai *tool*. Buat MCP server kecil yang membungkus `broker.py`, daftarkan di `~/.codeium/windsurf/mcp_config.json`:
   ```json
   {
     "mcpServers": {
       "mt5": {
         "command": "python",
         "args": ["C:\\proyek\\mcp_mt5.py"],
         "env": { "MT5_LOGIN": "...", "MT5_SERVER": "..." }
       }
     }
   }
   ```
   Batasi tool-nya: sediakan `get_price`, `get_positions`, `dry_run_order`. **Jangan** ekspos `order_send` live ke AI sebelum berbulan-bulan diuji.

---

## Tahap 4 — VPS mandiri di Alibaba Cloud (ECS)

1. Buat instance **ECS Windows Server 2022**, minimal 2 vCPU / 4 GB / 40 GB SSD; pilih region terdekat ke server broker (biasanya Singapura/Tokyo untuk broker Asia — cek `mt5.terminal_info().community_account`/ping).
2. Security Group: buka **RDP 3389 hanya dari IP Anda**, SSH 22 kalau perlu, dan **jangan** buka port 8000 ke publik (pakai SSH tunnel).
3. Di VPS: install MT5 + Python, ulangi Tahap 1, login akun demo.
4. Jadikan bot layanan yang auto-restart: NSSM (`nssm install Superkomputer ...`) atau Task Scheduler *At startup, run whether user logged on or not*.
5. Nyalakan OSS/snapshot backup harian + log rotasi.

Tunnel aman dari laptop:
```bash
ssh -L 8000:localhost:8000 admin@IP_VPS
```

---

## Tahap 5 — Integrasi Qwen sebagai lapis analisis

```python
from openai import OpenAI  # DashScope kompatibel-OpenAI
client = OpenAI(api_key=os.environ["DASHSCOPE_API_KEY"],
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
resp = client.chat.completions.create(model="qwen-plus", messages=[...])
```
Aturan main: LLM hanya memberi **skor/konteks** (misal ringkasan berita, klasifikasi rezim pasar) yang masuk sebagai satu fitur ke `strategy.py`. Keputusan order tetap deterministik di kode Anda, agar bisa di-backtest dan tidak berubah-ubah.

---

## Tahap 6 — Uji, baru live

1. Unit test `strategy.py` + `risk.py` (pytest, mock harga).
2. Backtest di Strategy Tester MT5 / data historis via `mt5.copy_rates_range`.
3. Demo forward-test minimal 4–8 minggu tanpa intervensi.
4. Live dengan lot terkecil + kill switch (`max_daily_loss` → tutup semua & stop).

## Checklist keamanan
- Kredensial MT5 & API key: hanya env var / Secret Manager, tidak di repo.
- Akun MT5 terpisah untuk eksperimen; jangan akun utama.
- Audit log setiap order (request + retcode) ke file harian.
- 2FA di akun Alibaba Cloud, RDP dibatasi IP.

---

### Yang saya butuhkan dari Anda untuk lanjut
1. Konfirmasi "QwenCloud" = Alibaba Cloud ECS + Qwen API, atau layanan lain (kirim link).
2. `Superkomputer.py` saat ini ada di mana? Repo `adhypglank/Study` masih kosong — kalau Anda push ke sana, saya bisa langsung refactor ke struktur Tahap 2 dan tulis unit test-nya.
3. Broker + simbol yang dipakai (untuk pemilihan region VPS dan spesifikasi order).
