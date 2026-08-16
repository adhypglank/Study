"""Polyglot bridge: map common commands from many languages into SPOK bahasa Indonesia.

The dictionary below is intentionally broad.  It does not perform full language
parsing; it recognises the first known keyword on each source line and emits an
analogous SPOK sentence that Charta can compile into Devanagari/Sanskrit.
"""

from __future__ import annotations

import re
from pathlib import Path


# Common command equivalents used by most languages.
_COMMON = {
    # Output / input
    "print": "MENAMPILKAN",
    "println": "MENAMPILKAN",
    "printf": "MENAMPILKAN",
    "puts": "MENAMPILKAN",
    "echo": "MENAMPILKAN",
    "writeln": "MENAMPILKAN",
    "write": "TULIS",
    "display": "MENAMPILKAN",
    "disp": "MENAMPILKAN",
    "show": "MENAMPILKAN",
    "log": "MENAMPILKAN",
    "nslog": "MENAMPILKAN",
    "io.puts": "MENAMPILKAN",
    "putstrln": "MENAMPILKAN",
    "input": "MEMBACA",
    "read": "MEMBACA",
    "readln": "MEMBACA",
    "readline": "MEMBACA",
    "read-host": "MEMBACA",
    "gets": "MEMBACA",
    "scanf": "MEMBACA",
    "cin": "MEMBACA",
    "accept": "MEMBACA",

    # Branching / looping
    "if": "JIKA",
    "elif": "JIKA_LAIN",
    "else": "JIKA_TIDAK",
    "for": "ULANG",
    "while": "ULANG_SELAMA",
    "do": "ULANG",
    "until": "ULANG_SELAMA",
    "loop": "ULANG",
    "foreach": "ULANG",
    "repeat": "ULANG",
    "for each": "ULANG",

    # Functions / procedures
    "def": "FUNGSI",
    "function": "FUNGSI",
    "func": "FUNGSI",
    "fn": "FUNGSI",
    "sub": "FUNGSI",
    "procedure": "FUNGSI",
    "proc": "FUNGSI",
    "method": "FUNGSI",
    "lambda": "FUNGSI",
    "delegate": "FUNGSI",

    # Return / exit
    "return": "MENGEMBALIKAN",
    "exit": "MENGEMBALIKAN",
    "quit": "MENGEMBALIKAN",
    "break": "MENGEMBALIKAN",
    "ret": "MENGEMBALIKAN",

    # Modules / imports
    "import": "MENGGUNAKAN",
    "include": "MENGGUNAKAN",
    "require": "MENGGUNAKAN",
    "using": "MENGGUNAKAN",
    "use": "MENGGUNAKAN",
    "library": "MENGGUNAKAN",
    "module": "MENGGUNAKAN",
    "namespace": "MENGGUNAKAN",
    "package": "MENGGUNAKAN",
    "from": "MENGGUNAKAN",

    # Types / data structures
    "class": "KELAS",
    "struct": "KELAS",
    "interface": "KELAS",
    "object": "KELAS",
    "type": "KELAS",
    "trait": "KELAS",
    "enum": "KELAS",
    "record": "KELAS",
    "protocol": "KELAS",

    # Error handling
    "try": "COBA",
    "catch": "KECUALI",
    "except": "KECUALI",
    "finally": "KECUALI",
    "throw": "KECUALI",
    "raises": "KECUALI",

    # Storage / assignments
    "let": "MENYIMPAN",
    "var": "MENYIMPAN",
    "val": "MENYIMPAN",
    "const": "MENYIMPAN",
    "final": "MENYIMPAN",
    "dim": "MENYIMPAN",
    "static": "MENYIMPAN",
    "auto": "MENYIMPAN",
    "mutable": "MENYIMPAN",
    "set": "MENYIMPAN",
    "move": "MEMINDAHKAN",
    "copy": "MENYALIN",
    "clone": "MENYALIN",
    "rename": "MEMINDAHKAN",

    # Deletion
    "delete": "MENGHAPUS",
    "remove": "MENGHAPUS",
    "drop": "MENGHAPUS",
    "free": "MENGHAPUS",
    "clear": "MENGHAPUS",
    "erase": "MENGHAPUS",
    "pop": "MENGHAPUS",

    # Insertion / addition
    "insert": "MEMASUKKAN",
    "append": "MEMASUKKAN",
    "push": "MEMASUKKAN",
    "add": "MEMASUKKAN",
    "enqueue": "MEMASUKKAN",

    # Update
    "update": "MEMPERBARUI",

    # Query
    "select": "MEMILIH",

    # File / I/O
    "open": "BUKA",
    "fopen": "BUKA",
    "close": "MENGHAPUS",
    "save": "TULIS",
    "fwrite": "TULIS",

    # Build / install
    "install": "PASANG",
    "setup": "PASANG",
    "build": "BANGUN",
    "make": "BANGUN",
    "compile": "BANGUN",

    # Execution
    "run": "MENJALANKAN",
    "execute": "MENJALANKAN",
    "exec": "MENJALANKAN",
    "call": "MENJALANKAN",
    "system": "MENJALANKAN",
    "perform": "MENJALANKAN",
    "start": "MENJALANKAN",
    "launch": "MENJALANKAN",
    "go": "MENJALANKAN",

    # Calculation
    "calculate": "MENGHITUNG",
    "compute": "MENGHITUNG",
    "sum": "MENGHITUNG",
    "count": "MENGHITUNG",
    "evaluate": "MENGHITUNG",

    # Security
    "chmod": "MENGAMANKAN",
    "secure": "MENGAMANKAN",
    "protect": "MENGAMANKAN",
    "encrypt": "MENGAMANKAN",
    "lock": "MENGAMANKAN",

    # Management
    "manage": "MENGELOLA",
    "handle": "MENGELOLA",
    "process": "MENGELOLA",

    # Communication
    "send": "MENGIRIM_LAPORAN",
    "emit": "MENGIRIM_LAPORAN",
    "publish": "MENGIRIM_LAPORAN",
    "report": "MENGIRIM_LAPORAN",

    # Verification
    "assert": "CEK",
    "test": "CEK",
    "check": "CEK",
    "verify": "CEK",
    "validate": "CEK",
}


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
        "from": "MENGGUNAKAN",
        "class": "KELAS",
        "try": "COBA",
        "except": "KECUALI",
        "with open": "BUKA",
        "open": "BUKA",
        "raise": "KECUALI",
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
        "from": "MENGGUNAKAN",
        "class": "KELAS",
        "try": "COBA",
        "catch": "KECUALI",
        "fetch": "BACA_PASAR",
        "console.error": "MENGIRIM_LAPORAN",
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
        "system.out.print": "MENAMPILKAN",
        "system.out.println": "MENAMPILKAN",
        "scanner": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "package": "MENGGUNAKAN",
        "class": "KELAS",
        "try": "COBA",
        "catch": "KECUALI",
    },
    "go": {
        "fmt.print": "MENAMPILKAN",
        "fmt.println": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "return": "MENGEMBALIKAN",
        "import": "MENGGUNAKAN",
        "func": "FUNGSI",
        "package": "MENGGUNAKAN",
    },
    "rust": {
        "println!": "MENAMPILKAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
        "use": "MENGGUNAKAN",
        "mod": "MENGGUNAKAN",
        "fn": "FUNGSI",
        "struct": "KELAS",
        "let": "MENYIMPAN",
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
        "select": "MEMILIH",
        "insert": "MEMASUKKAN",
        "update": "MEMPERBARUI",
        "delete": "MENGHAPUS",
        "create": "BANGUN",
        "drop": "MENGHAPUS",
    },
    "mql5": {
        "ordersend": "KIRIM_PESANAN",
        "orderclose": "TUTUP_PESANAN",
        "ima": "HITUNG_MA",
        "ontick": "SAAT_TIK",
        "marketinfo": "BACA_PASAR",
        "symbol": "SIMBOL",
        "print": "MENAMPILKAN",
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
        "<script": "MENGGUNAKAN",
    },
    "css": {
        "display": "MENAMPILKAN",
        "color": "GAYA",
        "background": "GAYA",
        "font": "GAYA",
        "margin": "GAYA",
    },
    # Additional languages (common keywords only)
    "typescript": _COMMON | {
        "console.log": "MENAMPILKAN",
        "fetch": "BACA_PASAR",
        "interface": "KELAS",
        "type": "KELAS",
    },
    "csharp": _COMMON | {
        "console.writeline": "MENAMPILKAN",
        "console.write": "MENAMPILKAN",
        "console.readline": "MEMBACA",
        "namespace": "MENGGUNAKAN",
    },
    "swift": _COMMON | {
        "print": "MENAMPILKAN",
        "readline": "MEMBACA",
        "import": "MENGGUNAKAN",
    },
    "kotlin": _COMMON | {
        "println": "MENAMPILKAN",
        "readline": "MEMBACA",
        "fun": "FUNGSI",
        "val": "MENYIMPAN",
        "var": "MENYIMPAN",
    },
    "lua": _COMMON | {
        "print": "MENAMPILKAN",
        "io.read": "MEMBACA",
        "require": "MENGGUNAKAN",
        "function": "FUNGSI",
    },
    "perl": _COMMON | {
        "print": "MENAMPILKAN",
        "use": "MENGGUNAKAN",
        "sub": "FUNGSI",
        "<>" : "MEMBACA",
    },
    "r": _COMMON | {
        "print": "MENAMPILKAN",
        "readline": "MEMBACA",
        "library": "MENGGUNAKAN",
        "source": "MENGGUNAKAN",
        "assign": "MENYIMPAN",
    },
    "matlab": _COMMON | {
        "disp": "MENAMPILKAN",
        "input": "MEMBACA",
        "function": "FUNGSI",
    },
    "scala": _COMMON | {
        "println": "MENAMPILKAN",
        "import": "MENGGUNAKAN",
        "object": "KELAS",
        "def": "FUNGSI",
    },
    "dart": _COMMON | {
        "print": "MENAMPILKAN",
        "import": "MENGGUNAKAN",
        "class": "KELAS",
    },
    "powershell": _COMMON | {
        "write-output": "MENAMPILKAN",
        "write-host": "MENAMPILKAN",
        "read-host": "MEMBACA",
        "import-module": "MENGGUNAKAN",
        "function": "FUNGSI",
    },
    "batch": {
        "echo": "MENAMPILKAN",
        "set": "MENYIMPAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "goto": "MENJALANKAN",
        "call": "MENJALANKAN",
        "exit": "MENGEMBALIKAN",
        "copy": "MENYALIN",
        "move": "MEMINDAHKAN",
        "del": "MENGHAPUS",
    },
    "objective-c": _COMMON | {
        "nslog": "MENAMPILKAN",
        "printf": "MENAMPILKAN",
        "scanf": "MEMBACA",
        "#import": "MENGGUNAKAN",
        "@interface": "KELAS",
        "@implementation": "KELAS",
    },
    "groovy": _COMMON | {
        "println": "MENAMPILKAN",
        "def": "FUNGSI",
    },
    "haskell": _COMMON | {
        "putstrln": "MENAMPILKAN",
        "getline": "MEMBACA",
        "import": "MENGGUNAKAN",
        "module": "MENGGUNAKAN",
        "let": "MENYIMPAN",
    },
    "lisp": _COMMON | {
        "print": "MENAMPILKAN",
        "read": "MEMBACA",
        "defun": "FUNGSI",
        "lambda": "FUNGSI",
    },
    "fsharp": _COMMON | {
        "printfn": "MENAMPILKAN",
        "printf": "MENAMPILKAN",
        "console.readline": "MEMBACA",
        "open": "MENGGUNAKAN",
        "let": "MENYIMPAN",
    },
    "fortran": _COMMON | {
        "print": "MENAMPILKAN",
        "read": "MEMBACA",
        "program": "MENGGUNAKAN",
        "stop": "MENGEMBALIKAN",
    },
    "cobol": {
        "display": "MENAMPILKAN",
        "accept": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "move": "MENYIMPAN",
        "add": "MENGHITUNG",
        "subtract": "MENGHITUNG",
        "multiply": "MENGHITUNG",
        "divide": "MENGHITUNG",
        "perform": "MENJALANKAN",
        "stop": "MENGEMBALIKAN",
        "exit": "MENGEMBALIKAN",
        "go": "MENJALANKAN",
    },
    "pascal": _COMMON | {
        "writeln": "MENAMPILKAN",
        "readln": "MEMBACA",
        "uses": "MENGGUNAKAN",
        "program": "MENGGUNAKAN",
        "begin": "BANGUN",
        "procedure": "FUNGSI",
    },
    "delphi": _COMMON | {
        "writeln": "MENAMPILKAN",
        "readln": "MEMBACA",
        "uses": "MENGGUNAKAN",
        "program": "MENGGUNAKAN",
        "procedure": "FUNGSI",
    },
    "ada": _COMMON | {
        "put_line": "MENAMPILKAN",
        "get": "MEMBACA",
        "with": "MENGGUNAKAN",
        "procedure": "FUNGSI",
    },
    "erlang": _COMMON | {
        "io:format": "MENAMPILKAN",
        "module": "MENGGUNAKAN",
        "export": "MENGEMBALIKAN",
        "spawn": "MENJALANKAN",
    },
    "elixir": _COMMON | {
        "io.puts": "MENAMPILKAN",
        "io.gets": "MEMBACA",
        "def": "FUNGSI",
        "defmodule": "MENGGUNAKAN",
        "defp": "FUNGSI",
    },
    "crystal": _COMMON | {
        "puts": "MENAMPILKAN",
        "require": "MENGGUNAKAN",
        "def": "FUNGSI",
    },
    "nim": _COMMON | {
        "echo": "MENAMPILKAN",
        "readline": "MEMBACA",
        "import": "MENGGUNAKAN",
        "proc": "FUNGSI",
    },
    "v": _COMMON | {
        "println": "MENAMPILKAN",
        "import": "MENGGUNAKAN",
        "fn": "FUNGSI",
    },
    "solidity": _COMMON | {
        "function": "FUNGSI",
        "require": "CEK",
        "emit": "MENGIRIM_LAPORAN",
        "event": "MENGIRIM_LAPORAN",
    },
    "julia": _COMMON | {
        "println": "MENAMPILKAN",
        "readline": "MEMBACA",
        "using": "MENGGUNAKAN",
        "import": "MENGGUNAKAN",
        "function": "FUNGSI",
    },
    "visual_basic": _COMMON | {
        "print": "MENAMPILKAN",
        "input": "MEMBACA",
        "sub": "FUNGSI",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "while": "ULANG_SELAMA",
        "return": "MENGEMBALIKAN",
    },
    "prolog": _COMMON | {
        "write": "MENAMPILKAN",
        "read": "MEMBACA",
        "consult": "MENGGUNAKAN",
        "assert": "MEMASUKKAN",
        "retract": "MENGHAPUS",
    },
    "assembly": {
        "mov": "MENYIMPAN",
        "push": "MEMASUKKAN",
        "pop": "MENGHAPUS",
        "call": "MENJALANKAN",
        "ret": "MENGEMBALIKAN",
        "jmp": "MENJALANKAN",
        "int": "MENJALANKAN",
        "add": "MENGHITUNG",
        "sub": "MENGHITUNG",
        "mul": "MENGHITUNG",
        "div": "MENGHITUNG",
    },
    "vhdl": {
        "entity": "KELAS",
        "architecture": "BANGUN",
        "signal": "MENYIMPAN",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "for": "ULANG",
        "process": "MENGELOLA",
        "report": "MENGIRIM_LAPORAN",
    },
    "verilog": {
        "module": "KELAS",
        "input": "MEMBACA",
        "output": "MENAMPILKAN",
        "wire": "MENYIMPAN",
        "always": "ULANG",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "assign": "MENYIMPAN",
        "initial": "BANGUN",
    },
    "scratch": {
        "say": "MENAMPILKAN",
        "ask": "MEMBACA",
        "when": "JIKA",
        "repeat": "ULANG",
        "forever": "ULANG",
        "broadcast": "MENGIRIM_LAPORAN",
        "go to": "MEMINDAHKAN",
    },
    "abap": {
        "write": "MENAMPILKAN",
        "read": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "data": "MENYIMPAN",
        "loop": "ULANG",
        "select": "MEMILIH",
        "update": "MEMPERBARUI",
        "insert": "MEMASUKKAN",
    },
    "rpg": {
        "dsply": "MENAMPILKAN",
        "read": "MEMBACA",
        "if": "JIKA",
        "else": "JIKA_TIDAK",
        "do": "ULANG",
        "return": "MENGEMBALIKAN",
        "callp": "MENJALANKAN",
    },
}


# SPOK predicate -> full SPOK sentence template.
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
    "MENJALANKAN": "SISTEM MENJALANKAN PROGRAM OTOMATIS",
    "MENYIMPAN": "SISTEM MENYIMPAN NILAI SECARA_AMAN",
    "MENGAMANKAN": "SISTEM MENGAMANKAN FILE SECARA_AMAN",
    "MENGELOLA": "SISTEM MENGELOLA DATA OTOMATIS",
    "MENGHITUNG": "SISTEM MENGHITUNG NILAI OTOMATIS",
    "EKSEKUSI_DUAL_ENTRY": "SISTEM EKSEKUSI_DUAL_ENTRY STRATEGI_AUTO_RBT OTOMATIS_24JAM",
    "MENGIRIM_LAPORAN": "SISTEM MENGIRIM_LAPORAN PESAN KE_EMAIL_PEMBUAT",
    "MEMINDAHKAN": "SISTEM MEMINDAHKAN FILE OTOMATIS",
    "MENYALIN": "SISTEM MENYALIN FILE OTOMATIS",
    "KIRIM_PESANAN": "BOT_RBT KIRIM_PESANAN ORDER DI_METATRADER5",
    "TUTUP_PESANAN": "BOT_RBT TUTUP_PESANAN ORDER DI_METATRADER5",
    "HITUNG_MA": "BOT_RBT HITUNG_MA ASET_RISIKO_75 DI_METATRADER5",
    "SAAT_TIK": "SISTEM SAAT_TIK PASAR OTOMATIS_24JAM",
    "BACA_PASAR": "SISTEM BACA_PASAR DATA DI_METATRADER5",
    "PINDAH_DIREKTORI": "SISTEM PINDAH_DIREKTORI FILE OTOMATIS",
    "KELAS": "SISTEM KELAS NAMA OTOMATIS",
    "HALAMAN": "SISTEM BANGUN HALAMAN OTOMATIS",
    "GAYA": "SISTEM MENAMPILKAN GAYA OTOMATIS",
    "TOMBOL": "SISTEM BANGUN TOMBOL OTOMATIS",
    "KLIK": "SISTEM KLIK TOMBOL OTOMATIS",
    "SIMBOL": "SISTEM BACA_PASAR SIMBOL DI_METATRADER5",
}


# Pre-compile keyword patterns for each supported language, sorted by descending length.
_COMPILED_PATTERNS: dict[str, list[tuple[re.Pattern, str]]] = {
    lang: [
        (re.compile(re.escape(kw), re.IGNORECASE), predicate)
        for kw, predicate in sorted(table.items(), key=lambda kv: -len(kv[0]))
    ]
    for lang, table in POLYGLOT.items()
}


def detect_language(source_path: str | Path) -> str:
    """Heuristic language detection from file extension."""
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
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
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".lua": "lua",
        ".pl": "perl",
        ".r": "r",
        ".matlab": "matlab",
        ".m": "matlab",
        ".scala": "scala",
        ".sc": "scala",
        ".dart": "dart",
        ".ps1": "powershell",
        ".bat": "batch",
        ".cmd": "batch",
        ".mm": "objective-c",
        ".groovy": "groovy",
        ".gy": "groovy",
        ".hs": "haskell",
        ".lisp": "lisp",
        ".cl": "lisp",
        ".fs": "fsharp",
        ".fsx": "fsharp",
        ".f90": "fortran",
        ".f95": "fortran",
        ".cob": "cobol",
        ".cobol": "cobol",
        ".cbl": "cobol",
        ".pas": "pascal",
        ".dpr": "delphi",
        ".adb": "ada",
        ".erl": "erlang",
        ".ex": "elixir",
        ".exs": "elixir",
        ".cr": "crystal",
        ".nim": "nim",
        ".v": "v",
        ".sol": "solidity",
        ".jl": "julia",
        ".vb": "visual_basic",
        ".pro": "prolog",
        ".asm": "assembly",
        ".s": "assembly",
        ".vhd": "vhdl",
        ".vhdl": "vhdl",
        ".sb3": "scratch",
        ".abap": "abap",
        ".rpgle": "rpg",
    }
    ext = Path(source_path).suffix.lower()
    # .v is ambiguous (V-lang vs Verilog); default to V-lang unless filename hints Verilog.
    if ext == ".v":
        name = Path(source_path).name.lower()
        if "verilog" in name or "rtl" in name or "design" in name:
            return "verilog"
        return "v"
    return mapping.get(ext, "python")


def _first_keyword(line: str, language: str) -> str | None:
    """Return the SPOK predicate for the first recognised keyword in a line."""
    for pattern, predicate in _COMPILED_PATTERNS.get(language, _COMPILED_PATTERNS["python"]):
        if pattern.search(line):
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
        if not line or line.startswith(("#", "//", "/*", "*", "--", "<!--", "{", "}")):
            continue
        keyword = _first_keyword(line, language)
        if keyword is None or keyword not in SPOK_TEMPLATES:
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
