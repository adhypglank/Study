#!/usr/bin/env python3
"""Build the ChartaRuntime binary for the current platform using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    spec = Path(__file__).with_name("ChartaRuntime.spec").resolve()
    if not spec.exists():
        print("[ERROR] ChartaRuntime.spec not found", file=sys.stderr)
        return 1

    if not shutil.which("pyinstaller"):
        print("[ERROR] pyinstaller not found; install with: pip install pyinstaller", file=sys.stderr)
        return 1

    env = os.environ.copy()
    # macOS universal2 can be requested via env var.
    if sys.platform == "darwin" and env.get("PYINSTALLER_TARGET_ARCH") not in ("x86_64", "arm64", "universal2"):
        env["PYINSTALLER_TARGET_ARCH"] = "universal2"

    cmd = [sys.executable, "-m", "PyInstaller", str(spec), "--clean", "--noconfirm"]
    print("[BUILD] Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=spec.parent, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
