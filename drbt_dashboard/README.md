# dRBT Multi-Bot Performance Dashboard

Visualisasi kinerja multi-bot (SuperSpeed / HyperSonic / HyperAgressive) dari MetaTrader 5,
dipisahkan per magic number sesuai `AUTO_RBT_STATUS.md`.

## Arsitektur
```
Windows (MT5 + MetaEditor)                 Mana saja (VPS/laptop/VM)
+---------------------------+   tunnel    +---------------------------+
| terminal MT5 (login)      |  cloudflared| dashboard.py (port 8050)  |
| mt5_bridge.py (port 5000) | ----------> | BRIDGE_URL=https://.../api|
+---------------------------+   /ngrok    +---------------------------+
```

## Cara pakai
1. **Di mesin Windows yang menjalankan MT5** (terminal harus terbuka & login):
   ```powershell
   pip install flask MetaTrader5
   python mt5_bridge.py
   ```
2. (Opsional, bila dashboard di mesin lain) expose bridge:
   `cloudflared.exe tunnel --url http://localhost:5000` — catat URL-nya.
3. **Dashboard** (di mana saja):
   ```bash
   pip install flask requests
   BRIDGE_URL=https://<tunnel>/api/overview python dashboard.py
   ```
   Buka http://localhost:8050
4. **Mode demo** tanpa MT5 (data simulasi): `DEMO=1 python dashboard.py`

## Keamanan
- Jangan expose bridge tanpa perlindungan: gunakan cloudflared Access/ngrok auth.
- Bridge hanya membaca (tidak ada endpoint order).
- Rotate API key yang pernah terkirim lewat chat/file.
