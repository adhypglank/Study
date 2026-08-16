# Charta Code Ultimate — Bekerja dalam Senyap

Paket siap pakai Charta Code: SPOK Indonesia → Aksara Sanskerta → Python / MQL5, dengan enkripsi AES-GCM dan dukungan 51 bahasa pemrograman.

## Isi Folder

| Folder / File | Fungsi |
|---|---|
| `src/` | Kode sumber utama: `ChartaRuntime.py`, `charta_runtime.py`, `charta_polyglot.py`, `charta_nirvana.py` (Jayacharta AI), `charta_protect.py`, `charta_mt5_bridge.py`, `charta_bridge.mqh`, `ChartaRuntime.spec`, `build.py`, `requirements.txt` |
| `examples/` | Contoh `ai.spok` dan `ai_module.py` |
| `docs/` | Laporan validasi 51 bahasa (`VALIDATION_REPORT.md`) |
| `bin/` | Tempat biner PyInstaller hasil build (terisi setelah `install.py` sukses) |
| `install.py` | Installer otomatis: install dependensi, buat kunci, build biner |
| `launch.py` | Peluncur "Bekerja dalam Senyap": compile file `.spok`/`.py`/dll ke `.cht` |
| `Bekerja_Dalam_Senyap.*` | Klik-dan-jalan untuk Windows (`.cmd`), Linux (`.sh`), macOS (`.command`) |
| `Install_Charta_Ultimate.*` | Klik-dan-jalan installer untuk masing-masing OS |

## Cara Install

### Windows

Klik dua kali `Install_Charta_Ultimate.cmd`.

### Linux / macOS

Buka terminal di folder ini, lalu:

```bash
./Install_Charta_Ultimate.sh
# atau di macOS klik dua kali Install_Charta_Ultimate.command
```

Atau langsung dengan Python:

```bash
python install.py
```

Installer akan:
1. Menginstall `requirements.txt`.
2. Membuat file `.env` berisi `CHARTA_MASTER_KEY` baru.
3. Mencoba build biner `ChartaRuntime` dengan PyInstaller (jika tersedia).

## Cara Pakai — Bekerja dalam Senyap

### Windows

Klik dua kali `Bekerja_Dalam_Senyap.cmd`.

### Linux / macOS

```bash
./Bekerja_Dalam_Senyap.sh
# atau di macOS klik dua kali Bekerja_Dalam_Senyap.command
```

Secara default file `src/program.spok` dikompilasi menjadi `charta_output.cht`.

### Opsi Lanjutan

```bash
# Mode senyap, compile AI SPOK ke .cht
python3 launch.py --senyap examples/ai.spok ai.cht

# Compile lalu ekspor ke Python
python3 launch.py --senyap --python examples/ai.spok ai.cht

# Compile lalu ekspor ke MQL5
python3 launch.py --senyap --mq5 src/program.spok program.cht
```

## Fitur Utama

- **SPOK Indonesia**: setiap baris perintah menggunakan pola Subyek-Predikat-Obyek-Keterangan.
- **Devanagari/Sanskerta**: setiap token SPOK dipetakan ke aksara Devanagari dengan IAST.
- **Enkripsi `.cht` / `.chrt`**: AES-GCM dengan kunci pribadi.
- **Polyglot 51 bahasa**: Python, JavaScript, TypeScript, C/C++, Java, Go, Rust, PHP, Ruby, SQL, MQL5, Bash, HTML, CSS, C#, Swift, Kotlin, Lua, Perl, R, Matlab, Scala, Dart, PowerShell, Batch, Objective-C, Groovy, Haskell, Lisp, F#, Fortran, COBOL, Pascal, Delphi, Ada, Erlang, Elixir, Crystal, Nim, V, Solidity, Julia, Visual Basic, Prolog, Assembly, VHDL, Verilog, Scratch, ABAP, RPG.
- **Jayacharta AI (`charta_nirvana`)**: perintah AI/ML seperti `SIAPKAN_DATA`, `LATIH_MODEL`, `INFERENSI`, `EVALUASI_MODEL`, `PREDIKSI`, `SIMPAN_MODEL` menjadi skrip Python scikit-learn.
- **MetaTrader 5 bridge**: `charta_mt5_bridge.py` + `charta_bridge.mqh` untuk komunikasi HTTP.
- **Anti-pencurian**: `charta_protect.py` membungkus file apa saja ke `.chrt` dengan enkripsi dan watermark; gagal dekripsi menghasilkan data kosong tanpa merusak perangkat.
- **Build biner**: PyInstaller menghasilkan `ChartaRuntime` untuk Windows, Linux, macOS x86_64, dan macOS arm64.

## Perintah ChartaRuntime

```bash
cd src
python3 ChartaRuntime.py kunci
python3 ChartaRuntime.py buat program.spok program.cht
python3 ChartaRuntime.py baca program.cht --format charta
python3 ChartaRuntime.py baca program.cht --format python
python3 ChartaRuntime.py baca program.cht --format mq5
python3 ChartaRuntime.py nirvana examples/ai.spok ai_module.py
python3 ChartaRuntime.py bungkus rahasia.py rahasia.py.chrt
python3 ChartaRuntime.py buka rahasia.py.chrt rahasia.py
python3 ChartaRuntime.py jembatan
```

## Validasi

Lihat `docs/VALIDATION_REPORT.md` untuk hasil pengujian 51 bahasa: 0 failures, semua output Charta mengandung aksara Devanagari valid.

## Keamanan

Jangan pernah mengunggah file `.env` atau kunci `CHARTA_MASTER_KEY` ke repositori publik. Gunakan `charta_protect.py` untuk membungkus file sensitif.

---

Hak Cipta © 2026 Adi Putra (Adhyp Glank).
