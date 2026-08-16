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

## Hasil Build .exe

Gunakan PyInstaller dengan spesifikasi yang sudah disediakan:

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

## Hak Cipta

Hak Cipta © 2026 Adi Putra (Adhyp Glank).
