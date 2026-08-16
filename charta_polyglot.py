"""Polyglot bridge: map common commands from many languages into SPOK bahasa Indonesia.

The dictionary below is intentionally compact.  It does not perform full language
parsing; it recognizes the first known keyword on each source line and emits an
analogous SPOK sentence that Charta can compile into Devanagari/Sanskrit.
"""

from __future__ import annotations

import re
from pathlib import Path


# keyword (language) -> SPOK predicate/object marker
POLYGLOT: dict[str, dict[str, str]] = {
    "python": {
        "print": "MENAMPILKAN",
        "input": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "elif": "JIKA_LAIN",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "def": "FUNGSI",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "from": "DARI",
        "class": "KELAS",
        "try": "COBA",
        "except": "KECUALI",
        "install": "PASANG",
        "build": "BANGUN",
        "test": "CEK",
    },
    "javascript": {
        "console.log": "MENAMPILKAN",
        "alert": "MENAMPILKAN",
        "prompt": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "function": "FUNGSI",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "from": "DARI",
        "class": "KELAS",
        "try": "COBA",
        "catch": "KECUALI",
        "fetch": "BACA_PASAR",
    },
    "c": {
        "printf": "MENAMPILKAN",
        "scanf": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "#include": "MENGGUNAKAN",
        "struct": "KELAS",
        "malloc": "MEMASUKKAN",
        "free": "MENGHAPUS",
    },
    "cpp": {
        "cout": "MENAMPILKAN",
        "cin": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "#include": "MENGGUNAKAN",
        "class": "KELAS",
    },
    "java": {
        "System.out.print": "MENAMPILKAN",
        "System.out.println": "MENAMPILKAN",
        "Scanner": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "class": "KELAS",
        "try": "COBA",
        "catch": "KECUALI",
    },
    "go": {
        "fmt.Print": "MENAMPILKAN",
        "fmt.Println": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "func": "FUNGSI",
        "package": "MODUL",
    },
    "rust": {
        "println!": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "use": "MENGGUNAKAN",
        "fn": "FUNGSI",
        "mod": "MODUL",
        "struct": "KELAS",
    },
    "php": {
        "echo": "MENAMPILKAN",
        "print": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "function": "FUNGSI",
        "return": "MENGEMBALIKAN",
        "include": "MENGGUNAKAN",
        "require": "MENGGUNAKAN",
    },
    "ruby": {
        "puts": "MENAMPILKAN",
        "print": "MENAMPILKAN",
        "gets": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "def": "FUNGSI",
        "return": "MENGEMBALIKAN",
        "require": "MENGGUNAKAN",
        "class": "KELAS",
    },
    "sql": {
        "SELECT": "MEMILIH",
        "FROM": "DARI",
        "WHERE": "DIMANA",
        "INSERT": "MEMASUKKAN",
        "UPDATE": "MEMPERBARUI",
        "DELETE": "MENGHAPUS",
        "CREATE": "BANGUN",
        "TABLE": "DAFTAR",
    },
    "mql5": {
        "OrderSend": "KIRIM_PESANAN",
        "OrderClose": "TUTUP_PESANAN",
        "iMA": "HITUNG_MA",
        "OnTick": "SAAT_TIK",
        "MarketInfo": "BACA_PASAR",
        "Symbol": "SIMBOL",
        "Print": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "#include": "MENGGUNAKAN",
    },
    "bash": {
        "echo": "MENAMPILKAN",
        "read": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "cd": "PINDAH_DIREKTORI",
        "cp": "MENYALIN",
        "mv": "MEMINDAHKAN",
        "rm": "MENGHAPUS",
        "install": "PASANG",
        "chmod": "MENGAMANKAN",
        "exit": "MENGEMBALIKAN",
    },
    "html": {
        "<html": "BANGUN",
        "<body": "BANGUN",
        "<div": "BANGUN",
        "<button": "TOMBOL",
        "<a": "KLIK",
        "<style": "GAYA",
    },
    "css": {
        "display": "MENAMPILKAN",
        "color": "GAYA",
        "background": "GAYA",
        "font": "GAYA",
        "margin": "GAYA",
    },
}


# SPOK predicate -> full SPOK sentence template
SPOK_TEMPLATES: dict[str, str] = {
    "MENAMPILKAN": "SISTEM MENAMPILKAN PESAN OTOMATIS",
    "MEMBACA": "SISTEM MEMBACA DATA OTOMATIS",
    "JIKA": "SISTEM JIKA KONDISI OTOMATIS",
    "JIKA_TIDAK": "SISTEM JIKA_TIDAK KONDISI OTOMATIS",
    "JIKA_LAIN": "SISTEM JIKA_LAIN KONDISI OTOMATIS",
    "ULANG": "SISTEM ULANG DAFTAR OTOMATIS",
    "ULANG_SELAMA": "SISTEM ULANG_SELAMA KONDISI OTOMATIS",
    "FUNGSI": "SISTEM FUNGSI NAMA OTOMATIS",
    "MENGEMBALIKAN": "SISTEM MENGEMBALIKAN NILAI OTOMATIS",
    "MENGGUNAKAN": "SISTEM MENGGUNAKAN MODUL OTOMATIS",
    "MENGHAPUS": "SISTEM MENGHAPUS DATA OTOMATIS",
    "MEMASUKKAN": "SISTEM MEMASUKKAN DATA OTOMATIS",
    "MEMPERBARUI": "SISTEM MEMPERBARUI DATA OTOMATIS",
    "MEMILIH": "SISTEM MEMILIH DATA OTOMATIS",
    "CEK": "SISTEM CEK KONDISI OTOMATIS",
    "COBA": "SISTEM COBA PROGRAM OTOMATIS",
    "KECUALI": "SISTEM KECUALI KONDISI OTOMATIS",
    "BUKA": "SISTEM BUKA FILE OTOMATIS",
    "TULIS": "SISTEM TULIS FILE OTOMATIS",
    "PASANG": "SISTEM PASANG APLIKASI OTOMATIS",
    "BANGUN": "SISTEM BANGUN APLIKASI OTOMATIS",
    "KIRIM_PESANAN": "BOT_RBT KIRIM_PESANAN ORDER DI_METATRADER5",
    "TUTUP_PESANAN": "BOT_RBT TUTUP_PESANAN ORDER DI_METATRADER5",
    "HITUNG_MA": "BOT_RBT HITUNG_MA ASET_RISIKO_75 DI_METATRADER5",
    "SAAT_TIK": "SISTEM SAAT_TIK PASAR OTOMATIS_24JAM",
    "BACA_PASAR": "SISTEM BACA_PASAR DATA DI_METATRADER5",
    "PINDAH_DIREKTORI": "SISTEM PINDAH_DIREKTORI FILE OTOMATIS",
    "MENYALIN": "SISTEM MENYALIN FILE OTOMATIS",
    "KELAS": "SISTEM KELAS NAMA OTOMATIS",
    "HALAMAN": "SISTEM BANGUN HALAMAN OTOMATIS",
    "GAYA": "SISTEM MENAMPILKAN GAYA OTOMATIS",
    "TOMBOL": "SISTEM BANGUN TOMBOL OTOMATIS",
    "KLIK": "SISTEM KLIK TOMBOL OTOMATIS",
    "SIMBOL": "SISTEM BACA_PASAR SIMBOL DI_METATRADER5",
}


def detect_language(source_path: str | Path) -> str:
    """Heuristic language detection from file extension."""
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "javascript",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".rb": "ruby",
        ".sql": "sql",
        ".mq5": "mql5",
        ".mqh": "mql5",
        ".sh": "bash",
        ".bash": "bash",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
    }
    ext = Path(source_path).suffix.lower()
    return mapping.get(ext, "python")


def _first_keyword(line: str, language: str) -> str | None:
    """Return the SPOK predicate for the first recognized keyword in a line."""
    table = POLYGLOT.get(language, POLYGLOT["python"])
    # Sort by length descending so longer keywords (e.g. console.log) match before shorter ones (log).
    for keyword, predicate in sorted(table.items(), key=lambda kv: -len(kv[0])):
        if re.search(re.escape(keyword), line, re.IGNORECASE):
            return predicate
    return None


def to_spok(source: str, language: str | None = None, source_path: str | Path | None = None) -> str:
    """Convert foreign source code lines into Indonesian SPOK sentences."""
    if language is None:
        if source_path is not None:
            language = detect_language(source_path)
        else:
            language = "python"
    sentences: list[str] = []
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "//", "/*", "*", "--", "<!--")):
            continue
        keyword = _first_keyword(line, language)
        if keyword is None or keyword not in SPOK_TEMPLATES:
            # If no keyword is recognized, preserve as a comment-like SPOK note.
            continue
        sentences.append(SPOK_TEMPLATES[keyword])
    return "\n".join(sentences)


def supported_languages() -> list[str]:
    return sorted(POLYGLOT.keys())


if __name__ == "__main__":
    sample = """print("Hello Charta")
if x > 0:
    for i in range(10):
        return i
import os
"""
    print(to_spok(sample, "python"))
