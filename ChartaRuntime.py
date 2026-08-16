"""ChartaRuntime — CLI khusus untuk membuat dan membaca file Charta.

Perintah utama (bahasa Indonesia):

    buat      : membuat .cht dari .spok, .py, .mq5, .js, .sql, dsb.
    baca      : membaca .cht (manifest atau export) / .chrt (peek)
    kunci     : menghasilkan kunci AES-256 baru
    bungkus   : membungkus file apa saja ke .chrt
    buka      : membuka .chrt menjadi file asli
    jembatan  : menjalankan HTTP bridge untuk MetaTrader 5
    nirvana   : menerjemahkan .spok AI/ML langsung ke .py

Contoh:

    CHARTA_MASTER_KEY=... python3 ChartaRuntime.py buat program.spok program.cht
    CHARTA_MASTER_KEY=... python3 ChartaRuntime.py baca program.cht --format charta
    CHARTA_MASTER_KEY=... python3 ChartaRuntime.py bungkus rahasia.py rahasia.py.chrt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import charta_polyglot
import charta_protect
import charta_runtime
import charta_mt5_bridge


def _stem(path: Path) -> str:
    return path.stem


def cmd_buat(args: Any) -> None:
    source: Path = args.sumber
    target: Path = args.target
    text = source.read_text(encoding="utf-8")
    ext = source.suffix.lower()

    if ext == ".spok":
        module = charta_runtime.compile_spok(text, source.stem)
    elif ext == ".py":
        module = charta_runtime.compile_python(text, source.stem)
    else:
        language = args.bahasa or charta_polyglot.detect_language(source)
        spok = charta_polyglot.to_spok(text, language, source)
        if not spok.strip():
            raise ValueError("Tidak ada perintah SPOK yang dapat diterjemahkan dari file sumber.")
        module = charta_runtime.compile_spok(spok, source.stem)

    charta_runtime.pack(module, target)
    print(f"[CHARTA RUNTIME] Berhasil membuat {target}")


def cmd_baca(args: Any) -> None:
    source: Path = args.file
    fmt: str = args.format
    ext = source.suffix.lower()

    if ext == ".chrt":
        if fmt == "manifest":
            manifest, _ = charta_protect.peek(source)
            import json
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
        else:
            _, plaintext = charta_protect.peek(source)
            try:
                print(plaintext.decode("utf-8"))
            except UnicodeDecodeError:
                print(f"[Berkas biner] {len(plaintext)} byte (tidak dapat ditampilkan sebagai teks)")
        return

    if ext == ".cht":
        if fmt == "manifest":
            charta_runtime.inspect_package(source)
            return
        module = charta_runtime.unpack(source)
        exporters = {
            "charta": charta_runtime.to_charta,
            "python": charta_runtime.to_python,
            "mq5": charta_runtime.to_mq5,
            "article": charta_runtime.to_article,
            "story": charta_runtime.to_story,
        }
        print(exporters[fmt](module), end="")
        return

    raise ValueError("File yang dibaca harus berupa .cht atau .chrt")


def cmd_kunci(args: Any) -> None:
    print(charta_runtime.generate_key())


def cmd_bungkus(args: Any) -> None:
    charta_protect.wrap(args.sumber, args.target)


def cmd_buka(args: Any) -> None:
    charta_protect.unwrap(args.sumber, args.target)


def cmd_jembatan(args: Any) -> None:
    charta_mt5_bridge.main()


def cmd_nirvana(args: Any) -> None:
    """Terjemahkan file .spok (khusus AI/ML) langsung ke Python."""
    source: Path = args.sumber
    target: Path = args.target
    text = source.read_text(encoding="utf-8")
    module = charta_runtime.compile_spok(text, source.stem)
    py_code = charta_runtime.to_python(module)
    target.write_text(py_code, encoding="utf-8")
    print(f"[JAYACHARTA AI] Berhasil membuat {target}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ChartaRuntime",
        description="Runtime Charta untuk membuat dan membaca file .cht/.chrt",
    )
    sub = parser.add_subparsers(dest="perintah", required=True)

    buat = sub.add_parser("buat", aliases=["create"], help="Buat file .cht dari sumber")
    buat.add_argument("sumber", type=Path, help="File sumber (.spok, .py, .mq5, .js, .sql, .html, dll)")
    buat.add_argument("target", type=Path, help="File .cht yang akan dibuat")
    buat.add_argument("--bahasa", type=str, default=None, help="Bahasa sumber (mis. python, mql5, sql)")
    buat.set_defaults(func=cmd_buat)

    baca = sub.add_parser("baca", aliases=["read"], help="Baca file .cht/.chrt")
    baca.add_argument("file", type=Path, help="File .cht atau .chrt")
    baca.add_argument(
        "--format",
        choices=["manifest", "charta", "python", "mq5", "article", "story"],
        default="manifest",
        help="Bentuk tampilan (default: manifest)",
    )
    baca.set_defaults(func=cmd_baca)

    kunci = sub.add_parser("kunci", aliases=["key"], help="Hasilkan kunci AES-256")
    kunci.set_defaults(func=cmd_kunci)

    bungkus = sub.add_parser("bungkus", aliases=["wrap"], help="Bungkus file ke .chrt")
    bungkus.add_argument("sumber", type=Path)
    bungkus.add_argument("target", type=Path)
    bungkus.set_defaults(func=cmd_bungkus)

    buka = sub.add_parser("buka", aliases=["unwrap"], help="Buka .chrt menjadi file asli")
    buka.add_argument("sumber", type=Path)
    buka.add_argument("target", type=Path)
    buka.set_defaults(func=cmd_buka)

    jembatan = sub.add_parser("jembatan", aliases=["bridge"], help="Jalankan HTTP bridge untuk MT5")
    jembatan.set_defaults(func=cmd_jembatan)

    nirvana = sub.add_parser("nirvana", aliases=["ai"], help="Terjemahkan .spok AI/ML langsung ke .py")
    nirvana.add_argument("sumber", type=Path, help="File .spok yang berisi perintah AI/ML")
    nirvana.add_argument("target", type=Path, help="File .py yang akan dihasilkan")
    nirvana.set_defaults(func=cmd_nirvana)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"[CHARTA ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
