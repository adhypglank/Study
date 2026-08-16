#!/usr/bin/env python3
"""Validate the Charta polyglot bridge against every supported language.

Run with a key to also generate .cht packages:

    CHARTA_MASTER_KEY=... python3 validate_all.py
"""

from __future__ import annotations

import base64
import os
import secrets
import sys
from pathlib import Path

# Add the repository root so the script can find the Charta modules.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import charta_polyglot
import charta_runtime

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
KEY_ENV = "CHARTA_MASTER_KEY"

# Preferred extension for each language; used for synthetic sample filenames.
LANG_EXT: dict[str, str] = {
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "c": ".c",
    "cpp": ".cpp",
    "java": ".java",
    "go": ".go",
    "rust": ".rs",
    "php": ".php",
    "ruby": ".rb",
    "sql": ".sql",
    "mql5": ".mq5",
    "bash": ".sh",
    "html": ".html",
    "css": ".css",
    "csharp": ".cs",
    "swift": ".swift",
    "kotlin": ".kt",
    "lua": ".lua",
    "perl": ".pl",
    "r": ".r",
    "matlab": ".m",
    "scala": ".scala",
    "dart": ".dart",
    "powershell": ".ps1",
    "batch": ".bat",
    "objective-c": ".m",
    "groovy": ".groovy",
    "haskell": ".hs",
    "lisp": ".lisp",
    "fsharp": ".fs",
    "fortran": ".f90",
    "cobol": ".cob",
    "pascal": ".pas",
    "delphi": ".dpr",
    "ada": ".adb",
    "erlang": ".erl",
    "elixir": ".ex",
    "crystal": ".cr",
    "nim": ".nim",
    "v": ".v",
    "solidity": ".sol",
    "julia": ".jl",
    "visual_basic": ".vb",
    "prolog": ".pro",
    "assembly": ".asm",
    "vhdl": ".vhd",
    "verilog": ".v",
    "scratch": ".sb3",
    "abap": ".abap",
    "rpg": ".rpgle",
}


def _has_devanagari(text: str) -> bool:
    return any("\u0900" <= c <= "\u097f" for c in text)


def _all_spok_tokens_in_dictionary(spok_text: str) -> bool:
    tokens = {word for line in spok_text.splitlines() for word in line.split()}
    missing = tokens - set(charta_runtime.SPOK_DICTIONARY)
    return not missing, missing


def main() -> int:
    if not os.environ.get(KEY_ENV):
        print(f"[WARN] {KEY_ENV} not set; .cht packages will be skipped.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "spok").mkdir(exist_ok=True)
    (OUT / "charta").mkdir(exist_ok=True)
    (OUT / "python").mkdir(exist_ok=True)
    (OUT / "mq5").mkdir(exist_ok=True)
    (OUT / "cht").mkdir(exist_ok=True)

    report_lines: list[str] = [
        "# Charta Code Final — Polyglot Validation Report",
        "",
        f"Languages tested: {len(charta_polyglot.POLYGLOT)}",
        f"SPOK dictionary entries: {len(charta_runtime.SPOK_DICTIONARY)}",
        f"SPOK templates: {len(charta_polyglot.SPOK_TEMPLATES)}",
        "",
        "| Language | Extension | SPOK lines | Charta lines | Valid Devanagari | Status |",
        "|---|---|---:|---:|:---:|:---:|",
    ]

    failures = 0
    for lang in sorted(charta_polyglot.POLYGLOT):
        ext = LANG_EXT.get(lang, ".txt")
        keywords = list(charta_polyglot.POLYGLOT[lang].keys())[:5]
        sample = "\n".join(keywords) + "\n"

        sample_path = OUT / "sources" / f"{lang}{ext}"
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.write_text(sample, encoding="utf-8")

        spok = charta_polyglot.to_spok(sample, lang)
        ok_tokens, missing = _all_spok_tokens_in_dictionary(spok)

        if not spok.strip():
            status = "NO_OUTPUT"
            failures += 1
        elif not ok_tokens:
            status = f"MISSING_TOKENS {missing}"
            failures += 1
        else:
            module = charta_runtime.compile_spok(spok, lang)
            charta = charta_runtime.to_charta(module)
            python_out = charta_runtime.to_python(module)
            mq5_out = charta_runtime.to_mq5(module)

            (OUT / "spok" / f"{lang}.spok").write_text(spok, encoding="utf-8")
            (OUT / "charta" / f"{lang}.charta.txt").write_text(charta, encoding="utf-8")
            (OUT / "python" / f"{lang}.py").write_text(python_out, encoding="utf-8")
            (OUT / "mq5" / f"{lang}.mq5").write_text(mq5_out, encoding="utf-8")

            valid_deva = _has_devanagari(charta)
            status = "PASS" if valid_deva else "NO_DEVANAGARI"
            if not valid_deva:
                failures += 1

            # Generate .cht if key is available.
            if os.environ.get(KEY_ENV):
                cht_path = OUT / "cht" / f"{lang}.cht"
                try:
                    charta_runtime.pack(module, cht_path)
                except Exception as exc:
                    status = f"PACK_ERROR: {exc}"
                    failures += 1

        charta_lines = len(charta.splitlines()) if 'charta' in dir() and charta else 0
        spok_lines = len(spok.splitlines()) if spok else 0
        valid_mark = "Yes" if status == "PASS" else "—"
        report_lines.append(
            f"| {lang} | {ext} | {spok_lines} | {charta_lines} | {valid_mark} | {status} |"
        )

    report_lines += [
        "",
        f"**Failures:** {failures}",
        "",
        "Notes:",
        "- Synthetic samples contain the first 5 mapped keywords for each language.",
        f"- SPOK output is validated to only contain tokens present in `charta_runtime.SPOK_DICTIONARY` ({len(charta_runtime.SPOK_DICTIONARY)} entries).",
        "- Charta (Devanagari) output is validated to contain at least one Devanagari codepoint.",
        "- `.cht` packages are generated only when `CHARTA_MASTER_KEY` is set and are git-ignored by the root `.gitignore`.",
    ]

    report_path = OUT / "VALIDATION_REPORT.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"[OK] Report written to {report_path}")
    print(f"[SUMMARY] {len(charta_polyglot.POLYGLOT)} languages tested, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
