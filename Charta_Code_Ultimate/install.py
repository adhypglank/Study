#!/usr/bin/env python3
"""Installer otomatis Charta Code Ultimate — cukup klik atau jalankan."""

from __future__ import annotations

import base64
import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
REQS = SRC / "requirements.txt"
ENV = ROOT / ".env"


def generate_key() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")


def run(cmd: list[str], cwd: Path | None = None) -> int:
    print(f"> {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    print("=== Charta Code Ultimate — Installer ===")
    print("Python:", sys.version.split()[0])

    # Ensure dependencies
    if REQS.exists():
        rc = run([sys.executable, "-m", "pip", "install", "-r", str(REQS)])
        if rc != 0:
            print("[ERROR] Gagal menginstall dependensi.")
            return rc
    else:
        print("[WARN] requirements.txt tidak ditemukan.")

    # Generate .env with a key if not present
    if not ENV.exists():
        key = generate_key()
        ENV.write_text(f"CHARTA_MASTER_KEY={key}\n", encoding="utf-8")
        print(f"[OK] Kunci baru dibuat di {ENV}")
    else:
        print(f"[OK] File {ENV} sudah ada, kunci tidak diganti.")

    # Optional PyInstaller build
    try:
        import PyInstaller  # noqa: F401
        print("[INFO] PyInstaller terdeteksi, membangun binary ChartaRuntime...")
        rc = run([sys.executable, "-m", "PyInstaller", str(SRC / "ChartaRuntime.spec"), "--clean", "--noconfirm"], cwd=SRC)
        if rc == 0:
            bin_dir = ROOT / "bin"
            bin_dir.mkdir(exist_ok=True)
            dist_dir = SRC / "dist"
            if dist_dir.exists():
                for f in dist_dir.iterdir():
                    if f.is_file():
                        dest = bin_dir / f.name
                        dest.write_bytes(f.read_bytes())
                        # Linux/macOS: pastikan binary dapat dieksekusi
                        if not f.name.endswith((".exe", ".cmd", ".bat")):
                            os.chmod(dest, 0o755)
            print(f"[OK] Binary tersalin ke bin/ dan tersedia di src/dist/")
        else:
            print("[WARN] PyInstaller build gagal; source tetap bisa dipakai langsung.")
    except ImportError:
        print("[INFO] PyInstaller tidak terpasang. Build binary di-skip; pakai `python src/ChartaRuntime.py`.")

    print("\n[OK] Charta Code Ultimate siap dipakai.")
    print("Luncurkan: python launch.py --senyap src/program.spok output.cht")
    print("atau klik script Bekerja_Dalam_Senyap.* di folder ini.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
