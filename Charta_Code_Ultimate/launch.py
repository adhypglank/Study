#!/usr/bin/env python3
"""Bekerja dalam Senyap — peluncur tanpa suara untuk Charta Code Ultimate.

Cara pakai:
    python launch.py --senyap src/program.spok output.cht
    python launch.py --senyap examples/ai.spok ai.cht
    python launch.py --python ai.cht ai.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
RUNTIME = SRC / "ChartaRuntime.py"
ENV = ROOT / ".env"


def load_env() -> None:
    if ENV.exists() and not os.environ.get("CHARTA_MASTER_KEY"):
        for line in ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("CHARTA_MASTER_KEY="):
                os.environ["CHARTA_MASTER_KEY"] = line.split("=", 1)[1].strip()


def run_silent(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    if capture:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return subprocess.run(cmd, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="BekerjaDalamSenyap",
        description="Peluncur senyap Charta Code Ultimate",
    )
    parser.add_argument("--senyap", action="store_true", help="Jalankan dalam mode senyap (hanya output penting)")
    parser.add_argument("--python", action="store_true", help="Setelah compile, ekspor ke Python")
    parser.add_argument("--mq5", action="store_true", help="Setelah compile, ekspor ke MQL5")
    parser.add_argument("input", type=Path, help="File sumber (.spok, .py, .mq5, dsb.)")
    parser.add_argument("output", type=Path, nargs="?", default=Path("charta_output.cht"), help="File .cht hasil")
    args = parser.parse_args()

    load_env()

    input_path = args.input.resolve()
    output_path = args.output.resolve()

    if not RUNTIME.exists():
        print(f"[ERROR] Tidak menemukan {RUNTIME}. Jalankan install.py dulu.")
        return 1

    # Compile
    cmd = [sys.executable, str(RUNTIME), "buat", str(input_path), str(output_path)]
    result = run_silent(cmd, capture=args.senyap)
    if result.returncode != 0:
        print(f"[ERROR] Compile gagal: {input_path}")
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode

    if not args.senyap:
        print(f"[OK] Tersimpan: {output_path}")

    # Optional exports
    if args.python:
        py_out = output_path.with_suffix(".py")
        with open(py_out, "w", encoding="utf-8") as fh:
            r = subprocess.run([sys.executable, str(RUNTIME), "baca", str(output_path), "--format", "python"], stdout=fh, cwd=ROOT)
        if r.returncode == 0:
            print(f"[OK] Python: {py_out}")
    if args.mq5:
        mq5_out = output_path.with_suffix(".mq5")
        with open(mq5_out, "w", encoding="utf-8") as fh:
            r = subprocess.run([sys.executable, str(RUNTIME), "baca", str(output_path), "--format", "mq5"], stdout=fh, cwd=ROOT)
        if r.returncode == 0:
            print(f"[OK] MQL5: {mq5_out}")

    if args.senyap:
        print("[OK] Selesai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
