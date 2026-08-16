#!/bin/bash
# Klik dua kali di macOS untuk menjalankan Charta Code: Bekerja dalam Senyap
set -e

cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[ERROR] Python 3 tidak ditemukan. Silakan install Python 3 dari python.org atau Homebrew."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "[INFO] Pertama kali menjalankan, menyiapkan kunci dan dependensi..."
    "$PYTHON" install.py
fi

"$PYTHON" launch.py --senyap src/program.spok charta_output.cht
