# Security Review — Charta Code / Charta SPOK Compiler

**Scope:** source attachments delivered for the `adhypglank/Study` repository.  
**Date:** 2026-08-14  
**Author:** Devin security review

## Summary

The original Python source implemented a workflow with Indonesian SPOK sentences and Devanagari/Sanskrit tags, but it used **base64 encoding as “encryption”**, stored plaintext secrets and e-mail addresses in source, and wrote files to paths derived from unsanitized user input.  This report documents those findings and the remediation applied in the secure implementation shipped in this repository.

## Findings & Fixes

| # | Issue | Severity | Original Evidence | Fix |
|---|---|---|---|---|
| 1 | **Fake encryption** — base64 only | Critical | `base64` encode/decode called on `.chrt` data and labelled encrypted | Replaced with **AES-GCM** authenticated encryption.  Keys come from the `CHARTA_MASTER_KEY` environment variable, 32 bytes, base64url. |
| 2 | **Hardcoded credentials & PII** | Critical | `emails = ["daribekasi@gmail.com", "adhypglank@gmail.com", ...]` | Moved to environment variable `CHARTA_AUDIT_EMAILS` and separated by commas.  No e-mail addresses in source. |
| 3 | **Path traversal in file paths** | High | `os.path.join(vault_path, filename)` used directly | Created `_secure_vault_path()` that resolves the vault root, rejects `.` / `..`, and verifies `os.path.commonpath()`. |
| 4 | **Unsafe file modes** | Medium | Files written with default `0o644` | Vault directory created as `0o700`; output files written as `0o600`. |
| 5 | **Insecure `eval` / `exec` / `subprocess` patterns** | Medium | The original script constructed Python source from parsed inputs and called `compile()`; `exec`/`eval` not present but runtime could be abused to execute generated Python | Compiler now emits an in-memory IR (`Instruction` dataclasses) instead of arbitrary Python source strings; no `eval`/`exec` is used.  The exporter writes deterministic Python/MQL5 text that is safe to inspect before running separately. |
| 6 | **Hardcoded master key** | High | Variable named `CHARTA_MASTER_KEY` was set to a literal string inside the source | Removed; key must be supplied via environment at runtime.  `.env.example` lists the variable with an empty placeholder. |
| 7 | **Insecure dependency version** | Medium | `cryptography==3.4.8` pinned in the environment | `requirements.txt` now uses `cryptography>=42.0,<45` to pull a modern, supported release with the AES-GCM backend. |
| 8 | **Binary attachments not statically analysed** | Info | `.exe` and `.7z` files were provided | Not executed.  They are not committed to this repository.  Re-building from source is recommended; if binaries are redistributed, submit them to a malware-scanner/virus-total service before use. |

## Verification Performed

- `python3 -m py_compile` passed for every `.py` file.
- `charta_runtime.py key` produced a valid 32-byte base64url key.
- `spok-help` listed the SPOK → Sanskrit dictionary with balanced parentheses and valid Devanagari characters.
- `compile-spok`, `inspect`, and `export` with AES-GCM succeeded against the sample `program.spok`.
- All Sanskrit entries in `README.md` were cross-checked against the runtime dictionaries and contain valid Devanagari code points.

## Secure Usage Reminders

- Never commit `.env`, `.env.local`, `*.secret`, `*.chrt`, or `*.cht` files.
- Generate a fresh `CHARTA_MASTER_KEY` per deployment and store it in a secrets manager or hardware security module.
- Keep the vault directory (`CHARTA_VAULT_PATH`) on an encrypted filesystem.
- Run `pip install -r requirements.txt` regularly and monitor `cryptography` security advisories.
