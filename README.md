# Charta Code — Bahasa SPOK Indonesia → Aksara Sanskerta

Bahasa Charta Code menyusun perintah komputer dengan pola **SPOK**:

- **S**ubyek
- **P**redikat
- **O**byek
- **K**eterangan

Setiap baris perintah ditulis dalam bahasa Indonesia, lalu diterjemahkan ke dalam **Aksara Devanagari Sanskerta** dan diberi penanda `AG<n>`. Runtime kemudian mengompilasinya ke bentuk perantara (IR), mengemasnya dalam file `.cht` yang dilindungi **AES-GCM**, dan bisa mengekspornya kembali sebagai teks Charta, Python, atau MQL5.

## Instalasi

```bash
pip install -r requirements.txt
```

Atau di Windows PowerShell:

```powershell
py -3 -m pip install -r requirements.txt
```

## Siapkan Kunci

Semua file Charta terenkripsi dengan kunci pribadi. Jangan pernah menyertakan kunci asli di repositori.

```powershell
# Windows
$env:CHARTA_MASTER_KEY = (py -3 .\charta_runtime.py key)
```

```bash
# Linux/macOS
export CHARTA_MASTER_KEY=$(python3 ./charta_runtime.py key)
```

Untuk integrasi email audit:

```powershell
$env:CHARTA_AUDIT_EMAILS = "audit@contoh.com"
```

## Cara Menulis Program Charta

Buat file teks, misalnya `program.spok`, dengan satu kalimat SPOK per baris:

```text
SISTEM MENJALANKAN STRATEGI_AUTO_RBT OTOMATIS_24JAM
BOT_RBT MENGELOLA ASET_RISIKO_75 DI_METATRADER5
SISTEM EKSEKUSI_DUAL_ENTRY STRATEGI_AUTO_RBT OTOMATIS_24JAM
PEMILIK MENGHITUNG BAGI_HASIL_85_15 OTOMATIS_24JAM
SISTEM MENGIRIM_LAPORAN LAPORAN_HARIAN KE_EMAIL_PEMBUAT
```

Setiap token SPOK dipisahkan spasi dan semua huruf akan dikonversi ke besar (uppercase) secara otomatis oleh kompilator.

## Cara Mengompilasi dan Mengekspor

```bash
python3 ./charta_runtime.py compile-spok ./program.spok ./program.cht
python3 ./charta_runtime.py inspect ./program.cht
python3 ./charta_runtime.py export ./program.cht charta
python3 ./charta_runtime.py export ./program.cht python
python3 ./charta_runtime.py export ./program.cht mq5
```

Hasil `export charta` akan terlihat seperti ini:

```text
AG1 पद तन्त्र चालयति आर-बी-टी-रणनीति अहोरात्रं इति
AG2 पद आर-बी-टी-यन्त्र प्रबन्धयति सम्पत्ति-७५% एम-क्यू-एल-मञ्चे इति
...
```

## ChartaRuntime — CLI Khusus Membuat & Membaca

Selain `charta_runtime.py` yang memiliki banyak subperintah teknis, tersedia `ChartaRuntime.py` sebagai CLI berbahasa Indonesia untuk membuat dan membaca file Charta:

```bash
python3 ./ChartaRuntime.py kunci
python3 ./ChartaRuntime.py buat program.spok program.cht
python3 ./ChartaRuntime.py baca program.cht --format charta
python3 ./ChartaRuntime.py buat sample.py sample.cht
python3 ./ChartaRuntime.py buat strategy.mq5 strategy.cht
python3 ./ChartaRuntime.py bungkus rahasia.py rahasia.py.chrt
python3 ./ChartaRuntime.py buka rahasia.py.chrt rahasia.py
python3 ./ChartaRuntime.py jembatan
```

## Jayacharta AI — Modul AI/ML

`Jayacharta AI` (`charta_nirvana`, जयचार्त — kemenangan dalam penciptaan kode) adalah modul AI/ML yang menerjemahkan perintah SPOK ke skrip Python scikit-learn. Tambahkan ke `program.spok` atau gunakan perintah `nirvana`:

```text
SISTEM SIAPKAN_DATA DATASET OTOMATIS
SISTEM LATIH_MODEL MODEL OTOMATIS
SISTEM INFERENSI DATASET OTOMATIS
SISTEM EVALUASI_MODEL MODEL OTOMATIS
SISTEM PREDIKSI HASIL OTOMATIS
SISTEM SIMPAN_MODEL MODEL OTOMATIS
```

```bash
python3 ./ChartaRuntime.py nirvana examples/ai.spok ai_module.py
# atau lewat .cht
python3 ./ChartaRuntime.py buat examples/ai.spok ai.cht
python3 ./ChartaRuntime.py baca ai.cht --format python
```

Hasilnya adalah skrip Python dengan `pandas`, `scikit-learn`, dan `joblib` yang dapat dijalankan di lingkungan yang memiliki dependensi tersebut. Predikat Jayacharta AI yang tersedia: `SIAPKAN_DATA`, `MUAT_MODEL`, `LATIH_MODEL`, `INFERENSI`, `PREDIKSI`, `EVALUASI_MODEL`, `SIMPAN_MODEL`.

## Hasil Build .exe

Gunakan PyInstaller dengan spesifikasi yang sudah disediakan. File `ChartaRuntime.spec` sekarang mengarah ke `ChartaRuntime.py` agar hasil `.exe` sama dengan CLI Python terbaru:

```powershell
py -3 -m PyInstaller ChartaRuntime.spec
```

File `ChartaRuntime.cmd` kemudian dapat dipakai untuk menjalankan `ChartaRuntime.exe` dari folder yang sama.

## Cara Kerja Singkat

1. **Parser SPOK** memecah kalimat menjadi Subyek, Predikat, Obyek, dan Keterangan.
2. **Kamus SPOK** menerjemahkan setiap kata ke Devanagari + IAST.
3. **IR (Intermediate Representation)** menyimpanstruktur kalimat dalam bentuk objek `Instruction`.
4. **`pack()`** mengenkripsi IR dengan `AESGCM` dan menyimpannya sebagai JSON envelope `.cht`.
5. **`unpack()`** memverifikasi autentikasi `AESGCM` dan mengembalikan IR ke memori.
6. **Eksporter** menghasilkan kembali teks Charta, Python, atau MQL5 tanpa mengeksekusi kode asal.

> **Catatan keamanan:** `.cht` adalah file terenkripsi, bukan “kode biner tak terdeteksi”. Enkripsi melindungi isi dari pembaca tanpa kunci, tetapi manifest dan metadata paket tetap terlihat. Ini lebih transparan dan lebih aman daripada obfuscation yang berusaha menyembunyikan diri dari alat keamanan.

---

## Tabel Padanan SPOK → Aksara Sanskerta

| SPOK | Devanagari | IAST | Kategori | Makna/Operasi |
|---|---|---|---|---|
| `SAYA` | अहम् | Aham | Subjek | Saya / pelaku |
| `KITA` | वयं | Vayam | Subjek | Kita |
| `SISTEM` | तन्त्र | Tantra | Subjek | Sistem |
| `BOT_RBT` | आर-बी-टी-यन्त्र | RBT-Yantra | Subjek | Robot/RBT |
| `PEMILIK` | स्वामी | Svāmī | Subjek | Pemilik |
| `MEMINDAHKAN` | स्थापयति | Sthāpayati | Predikat | Memindahkan / menempatkan |
| `MENYIMPAN` | रक्षति | Rakṣati | Predikat | Menyimpan / melindungi |
| `MENJALANKAN` | चालयति | Cālayati | Predikat | Menjalankan |
| `MEMBACA` | पठति | Paṭhati | Predikat | Membaca |
| `MENGAMANKAN` | गोपयति | Gopayati | Predikat | Mengamankan |
| `MENGELOLA` | प्रबन्धयति | Prabandhayati | Predikat | Mengelola |
| `MENGHITUNG` | गणयति | Gaṇayati | Predikat | Menghitung |
| `EKSEKUSI_DUAL_ENTRY` | द्वि-प्रवेश-करोति | Dvi-Praveśa-Karoti | Predikat | Eksekusi dual entry |
| `MENGIRIM_LAPORAN` | विवरणं-प्रेषयति | Vivaraṇaṁ-Preṣayati | Predikat | Mengirim laporan |
| `FILE` | सञ्चिका | Sañcikā | Objek | File |
| `DATA` | दत्तांश | Dattāṁśa | Objek | Data |
| `KODE` | सङ्केत | Saṅketa | Objek | Kode |
| `PROGRAM` | प्रणाली | Praṇālī | Objek | Program |
| `STRATEGI_AUTO_RBT` | आर-बी-टी-रणनीति | RBT-Raṇanīti | Objek | Strategi Auto RBT |
| `ASET_RISIKO_75` | सम्पत्ति-७५% | Sampatti-75% | Objek | Aset risiko 75% |
| `BIAYA_INAP_16.5` | रात्रि-शुल्कम्-१६.५ | Rātri-Śulkam-16.5 | Objek | Biaya inap 16.5 |
| `BAGI_HASIL_85_15` | लाभ-८५-१५ | Lābha-85-15 | Objek | Bagi hasil 85/15 |
| `LAPORAN_HARIAN` | दैनिक-विवरण | Dainika-Vivaraṇa | Objek | Laporan harian |
| `OTOMATIS` | स्वयमेव | Svayameva | Keterangan | Otomatis |
| `OTOMATIS_24JAM` | अहोरात्रं-स्वयमेव | Ahorātraṁ-Svayameva | Keterangan | Otomatis 24 jam |
| `SECARA_AMAN` | सुरक्षितरूपेण | Surakṣitarūpeṇa | Keterangan | Secara aman |
| `DI_METATRADER5` | एम-क्यू-एल-मञ्चे | MQL-Mañce | Keterangan | Di MetaTrader 5 |
| `KE_EMAIL_PEMBUAT` | अधिप्-इमेल-दिशि | Adhyp-Email-Diśi | Keterangan | Ke email pembuat |
| `KE_DRIVE_D` | ड्राइव-ड-दिशि | Drive-D-Diśi | Keterangan | Ke drive D |
| `DI_CLOUD` | मेघे | Meghe | Keterangan | Di cloud |

### Catatan Validasi Aksara

- Semua pasangan kata SPOK memiliki setidaknya satu aksara Devanagari (`U+0900–U+097F`), sehingga valid secara visual sebagai aksara Sanskerta.
- Tidak ada spasi di dalam tanda kurung IAST pada tabel di atas; spasi yang ada pada berkas asli (`RBT-Ran niti` dan `MQL-Man ce`) telah diperbaiki agar tidak memecah satu token SPOK menjadi dua token saat digabungkan dalam satu baris Charta.
- Beberapa IAST telah diseragamkan dengan tanda diakritik panjang/muria (mis. `Svāmī`, `Cālayati`, `Rakṣati`, `Prabandhayati`, `Gaṇayati`, `Dattāṁśa`, `Saṅketa`, `Praṇālī`, `Surakṣitarūpeṇa`).

---

## Tabel Operator IR (Intermediate Representation)

| Operator | Sanskerta | IAST | Makna |
|---|---|---|---|
| `assign` | न्यासः | Nyāsaḥ | Penugasan |
| `call` | आह्वानम् | Āhvānam | Pemanggilan |
| `compare` | तुलना | Tulanā | Perbandingan |
| `constant` | मूल्यम् | Mūlyam | Konstanta / nilai |
| `expression` | अभिव्यक्तिः | Abhivyaktiḥ | Ekspresi / kalkulasi |
| `function` | कार्यं | Kāryam | Fungsi |
| `if` | यदि | Yadi | Kondisi jika |
| `module` | प्रणाली | Praṇālī | Modul |
| `name` | नाम | Nāma | Nama / variabel |
| `return` | प्रतिनिवर्तनम् | Pratinivartanam | Pengembalian nilai |
| `spok` | वाक्यम् | Vākyam | Satu kalimat SPOK |

## Polyglot: Menerjemahkan Banyak Bahasa ke SPOK

Charta Runtime kini dapat membaca cuplikan dari banyak bahasa dan mengubahnya menjadi kalimat SPOK bahasa Indonesia, lalu ke aksara Sanskerta, lalu ke Python dan `.cht`.

```bash
python3 ./charta_runtime.py translate-code ./sample.py
python3 ./charta_runtime.py compile-polyglot ./sample.py ./sample.cht
python3 ./charta_runtime.py polyglot-help
```

Bahasa yang didukung: **51 bahasa pemrograman**, dari Python, JavaScript/TypeScript, C/C++, Java, Go, Rust, PHP, Ruby, SQL, MQL5, Bash, HTML, CSS, C#, Swift, Kotlin, Lua, Perl, R, Matlab, Scala, Dart, PowerShell, Batch, Objective-C, Groovy, Haskell, Lisp, F#, Fortran, COBOL, Pascal, Delphi, Ada, Erlang, Elixir, Crystal, Nim, V, Solidity, Julia, Visual Basic, Prolog, Assembly, VHDL, Verilog, Scratch, ABAP, hingga RPG.

Contoh dari Python:

```python
print("Hello Charta")
if x > 0:
    for i in range(10):
        return i
import os
```

Akan diterjemahkan ke SPOK:

```text
SISTEM MENAMPILKAN PESAN OTOMATIS
SISTEM JIKA KONDISI OTOMATIS
SISTEM ULANG DAFTAR OTOMATIS
SISTEM MENGEMBALIKAN NILAI OTOMATIS
SISTEM MENGGUNAKAN MODUL OTOMATIS
```

Dari MQL5:

```mql5
void OnTick() {
   OrderSend(...);
   int ma = iMA(Symbol(), PERIOD_H1, 14, 0, MODE_SMA, PRICE_CLOSE);
}
```

Menjadi:

```text
SISTEM SAAT_TIK PASAR OTOMATIS_24JAM
BOT_RBT KIRIM_PESANAN ORDER DI_METATRADER5
SISTEM BACA_PASAR SIMBOL DI_METATRADER5
```

## Menulis Ulang Kode sebagai Artikel atau Cerita

Setiap `.cht` dapat diekspor sebagai prosa bahasa Indonesia.

```bash
python3 ./charta_runtime.py export ./program.cht article
python3 ./charta_runtime.py export ./program.cht story
```

- `article` menghasilkan artikel teknis yang menjelaskan tiap langkah eksekusi.
- `story` menghasilkan narasi fiksi singkat yang menggambarkan jalannya program seolah sebuah kisah.

## Integrasi MetaTrader 5 / MQL5

1. Hasilkan file `.mq5`:

```bash
python3 ./charta_runtime.py export ./program.cht mq5
```

2. Kompilasi di MetaEditor. File yang dihasilkan otomatis menyertakan `#include <charta_bridge.mqh>`.
3. Jalankan bridge Python di lokal:

```bash
CHARTA_VAULT_PATH=./ CHARTA_MASTER_KEY=... python3 ./charta_mt5_bridge.py
```

4. Tambahkan URL `http://127.0.0.1:15555` ke **MetaTrader 5 → Tools → Options → Expert Advisors → Allow WebRequest for listed URL**.

Cara kerja bridge:

- MetaTrader 5 memanggil `ChartaRequest()` dari `charta_bridge.mqh`.
- `charta_mt5_bridge.py` membaca paket `.cht` secara terenkripsi di memori dan mengembalikan sinyal SPOK sebagai JSON.
- MQL5 menerima JSON, mengekstrak teks SPOK, lalu mengirim `ack` supaya bridge melanjutkan ke instruksi berikutnya.
- Isi biner `.cht` tidak pernah dikirim ke MetaTrader; hanya keputusan teks SPOK yang dikirim, sehingga MetaTrader dapat membaca sinyal tanpa bisa menampilkan/membuang paket asli.

## Perlindungan File dan Anti-Pencurian

`charta_protect.py` membungkus file asli (kode, konfigurasi, model, dll.) menjadi file `.chrt` yang tidak dapat dibaca, disalin, atau ditampilkan tanpa `CHARTA_MASTER_KEY`.

```bash
CHARTA_MASTER_KEY=... python3 ./charta_protect.py wrap rahasia.py rahasia.py.chrt
CHARTA_MASTER_KEY=... python3 ./charta_protect.py unwrap rahasia.py.chrt rahasia.py
```

Jika kunci salah atau file dirusak, output dihasilkan kosong dan muncul pesan *"Kunci salah atau file telah dirusak. Output dikosongkan."* — **tanpa memaksa perangkat restart atau merusak sistem**. Keamanan dibangun dari enkripsi AES-GCM + watermark `CHARTA_OWNER` + hash SHA-256, bukan dari tindakan merusak perangkat.

## Daftar Perintah CLI

| Perintah | Fungsi |
|---|---|
| `key` | Hasilkan kunci AES-256 acak |
| `formats` | Tampilkan format dan adapter yang didaftarkan |
| `spok-help` | Bantuan pola SPOK dan tabel Sanskerta |
| `polyglot-help` | Daftar bahasa asing yang didukung |
| `inspect <cht>` | Lihat metadata `.cht` tanpa dekripsi kode |
| `compile-python <py> <cht>` | Kompilasi subset Python ke `.cht` |
| `compile-spok <spok> <cht>` | Kompilasi SPOK bahasa Indonesia ke `.cht` |
| `compile-polyglot <src> <cht>` | Kompilasi Python/JS/C/MQL5/SQL/HTML/CSS/... ke `.cht` |
| `translate-code <src>` | Tampilkan SPOK hasil terjemahan tanpa kompilasi |
| `export <cht> <charta/python/mq5/article/story>` | Ekspor `.cht` ke format pilihan |
| `charta_protect.py wrap <in> <out.chrt>` | Bungkus file asli ke `.chrt` |
| `charta_protect.py unwrap <in.chrt> <out>` | Pulihkan file dari `.chrt` |
| `charta_mt5_bridge.py` | HTTP bridge untuk MetaTrader 5 |

## Build Binary Mandiri (Windows, Linux, macOS)

`ChartaRuntime` dapat dibuat menjadi binary mandiri untuk Windows, Linux, dan macOS menggunakan PyInstaller. Untuk macOS disediakan dua artefak: `x86_64` dan `arm64`, karena beberapa dependensi (mis. `cryptography`/`cffi`) tidak menyediakan wheel universal2.

### Lokal

```bash
pip install pyinstaller
python3 build.py
```

Hasil ada di `dist/ChartaRuntime` (Linux/macOS) atau `dist/ChartaRuntime.exe` (Windows).

### GitHub Actions

Workflow `.github/workflows/build_charta.yml` otomatis membangun binary untuk setiap platform:

- `ChartaRuntime-ubuntu-latest`
- `ChartaRuntime-windows-latest`
- `ChartaRuntime-macos-arm64`
- `ChartaRuntime-macos-x86_64`

Untuk macOS, setiap job mengatur `PYINSTALLER_TARGET_ARCH` ke arsitektur runner (`arm64` atau `x86_64`).

## Hak Cipta

Hak Cipta © 2026 Adi Putra (Adhyp Glank).
