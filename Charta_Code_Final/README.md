# Charta Code Final

Folder ini berisi hasil validasi polyglot Charta Runtime untuk puluhan bahasa pemrograman.

## Struktur

- `validate_all.py` — skrip validasi otomatis untuk seluruh bahasa yang didukung.
- `outputs/`
  - `sources/` — cuplikan sintetis per bahasa.
  - `spok/` — terjemahan ke kalimat SPOK bahasa Indonesia.
  - `charta/` — keluaran aksara Devanagari/Sanskerta.
  - `python/` — keluaran export Python.
  - `mq5/` — keluaran export MQL5.
  - `cht/` — paket `.cht` terenkripsi (dihasilkan hanya jika `CHARTA_MASTER_KEY` di-set).
  - `VALIDATION_REPORT.md` — ringkasan hasil uji.

## Cara Menjalankan

```bash
# Tanpa membuat .cht (hanya SPOK + Charta):
python3 Charta_Code_Final/validate_all.py

# Dengan .cht terenkripsi:
export CHARTA_MASTER_KEY=$(python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())")
python3 Charta_Code_Final/validate_all.py
```

## Membaca/Membuat File Charta Secara Manual

```bash
python3 ChartaRuntime.py buat Charta_Code_Final/outputs/spok/python.spok python.cht
python3 ChartaRuntime.py baca python.cht --format charta
```
