#!/bin/bash
# Peluncur Bekerja dalam Senyap untuk Linux/macOS
cd "$(dirname "$0")" || exit 1
python3 launch.py --senyap src/program.spok charta_output.cht
