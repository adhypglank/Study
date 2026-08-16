# Dokumentasi Charta Code Ultimate

## 1. Visi

Charta Code adalah bahasa pemrograman general-purpose yang menggunakan kalimat bahasa Indonesia berpola **SPOK** (Subyek-Predikat-Obyek-Keterangan). Setiap baris diterjemahkan ke aksara **Devanagari/Sanskerta** sebagai representasi visual, lalu dikompilasi ke Intermediate Representation (IR), dienkripsi sebagai `.cht`/`.chrt`, dan dapat diekspor kembali ke Python atau MQL5.

## 2. Arsitektur

```
SPOK (Indonesia)
       ↓
SPOK_DICTIONARY → Devanagari + IAST
       ↓
IR (Instruction: op, data, sanskrit)
       ↓
pack() → AES-GCM → .cht
       ↓
to_charta() / to_python() / to_mq5()
```

### Komponen Inti

| File | Tugas |
|---|---|
| `charta_runtime.py` | Parser, IR, enkripsi `.cht`, eksport Charta/Python/MQL5/artikel/cerita |
| `charta_polyglot.py` | Penerjemah 51 bahasa pemrograman ke SPOK |
| `charta_nirvana.py` | **Jayacharta AI** — SPOK AI/ML → Python scikit-learn |
| `charta_protect.py` | Bungkus file apa saja ke `.chrt` dengan AES-GCM + watermark |
| `charta_mt5_bridge.py` | HTTP bridge dua arah untuk MetaTrader 5 |
| `charta_bridge.mqh` | Header MQL5 untuk membaca sinyal Charta |
| `ChartaRuntime.py` | CLI berbahasa Indonesia untuk buat/baca/bungkus/buka/jembatan/nirvana |

## 3. SPOK & Aksara Sanskerta

Setiap kata SPOK memiliki padanan Devanagari dalam format `अक्षर (IAST)`. Runtime menggunakan `_deva()` untuk membersihkan tanda kurung IAST saat merakit output akhir.

Contoh:

```text
SISTEM MENJALANKAN STRATEGI_AUTO_RBT OTOMATIS_24JAM
```

Menjadi:

```text
AG1 पद तन्त्र चालयति आर-बी-टी-रणनीति अहोरात्रं-स्वयमेव इति
```

## 4. Polyglot

`charta_polyglot.POLYGLOT` memetakan keyword dari 51 bahasa ke predikat SPOK. Proses deteksi bahasa dilakukan dari ekstensi file, lalu string source diproses dengan regex yang sudah dikompilasi.

Contoh:

```bash
python3 src/charta_runtime.py compile-polyglot sample.py sample.cht
```

## 5. Jayacharta AI

`charta_nirvana` menyediakan predikat AI/ML:

- `SIAPKAN_DATA`
- `MUAT_MODEL`
- `LATIH_MODEL`
- `INFERENSI`
- `PREDIKSI`
- `EVALUASI_MODEL`
- `SIMPAN_MODEL`

Contoh `.spok`:

```text
SISTEM SIAPKAN_DATA DATASET OTOMATIS
SISTEM LATIH_MODEL MODEL OTOMATIS
SISTEM INFERENSI DATASET OTOMATIS
SISTEM EVALUASI_MODEL MODEL OTOMATIS
SISTEM PREDIKSI HASIL OTOMATIS
SISTEM SIMPAN_MODEL MODEL OTOMATIS
```

Hasil Python-nya menggunakan `pandas`, `scikit-learn`, dan `joblib`.

## 6. Enkripsi & Keamanan

- `.cht` dienkripsi dengan `AESGCM` menggunakan kunci 32 byte base64 dari `CHARTA_MASTER_KEY`.
- `.chrt` (anti-pencurian) adalah wrapper umum untuk file apa saja dengan manifest JSON dan ciphertext AES-GCM.
- Saat kunci salah, output adalah data kosong (zero-leak) tanpa memaksa restart atau merusak perangkat.

## 7. MetaTrader 5 Bridge

`charta_mt5_bridge.py` menjalankan server HTTP ringan. MetaTrader 5 (`.mq5`/`.mqh`) mengirim data pasar dan menerima sinyal SPOK JSON dari Charta tanpa pernah membuka file `.cht` biner.

## 8. Build Binary

Spesifikasi `src/ChartaRuntime.spec` mendukung `PYINSTALLER_TARGET_ARCH`. CI membangun:

- `ChartaRuntime-ubuntu-latest`
- `ChartaRuntime-windows-latest`
- `ChartaRuntime-macos-arm64`
- `ChartaRuntime-macos-x86_64`

Catatan: macOS universal2 tidak digunakan karena wheel `cryptography`/`cffi` tidak tersedia dalam bentuk fat binary.

## 9. Paket Ultimate

`Charta_Code_Ultimate` dirancang agar Charta Code dapat diinstall dan dijalankan dengan klik ganda:

- `install.py` — install dependensi, generate kunci, build biner.
- `launch.py` — peluncur "Bekerja dalam Senyap".
- `Install_Charta_Ultimate.*` — klik-dan-jalan installer per OS.
- `Bekerja_Dalam_Senyap.*` — klik-dan-jalan launcher per OS.

## 10. Validasi

`src/../Charta_Code_Final/validate_all.py` menguji 51 bahasa. Hasil terakhir: **51 bahasa, 0 failures**, semua output Charta mengandung aksara Devanagari.

---

Hak Cipta © 2026 Adi Putra (Adhyp Glank).
