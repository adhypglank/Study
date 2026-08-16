#!/bin/bash
# Klik dua kali di macOS untuk menjalankan Charta Code: Bekerja dalam Senyap
cd "$(dirname "$0")" || exit 1
python3 launch.py --senyap src/program.spok charta_output.cht
