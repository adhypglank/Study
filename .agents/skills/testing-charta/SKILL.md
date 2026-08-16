---
name: Testing the Charta SPOK CLI and Engine
scope: When testing the Charta SPOK runtime, ChartaLocalVault, or ChartaSPOKCompiler in /home/ubuntu/repos/Study
description: End-to-end CLI and API verification for the Charta SPOK compiler, AES-GCM packaging, exporters, and security controls.
---

# Charta Testing Skill

## Devin Secrets Needed
- `CHARTA_MASTER_KEY` — generated per test run with `python3 charta_runtime.py key`; do NOT commit it.
- Optional audit emails in `CHARTA_AUDIT_EMAILS` only if exercising the `ChartaVirtualMachine` email path.

## One-time setup
```bash
cd /home/ubuntu/repos/Study
pip install -r requirements.txt   # cryptography>=42.0,<45
```

## Standard test sequence
1. Generate a fresh key:
   ```bash
   export CHARTA_MASTER_KEY=$(python3 charta_runtime.py key)
   ```
2. Verify SPOK help renders Devanagari:
   ```bash
   python3 charta_runtime.py spok-help
   ```
3. Compile `program.spok`:
   ```bash
   python3 charta_runtime.py compile-spok program.spok program.cht
   ```
4. Inspect manifest:
   ```bash
   python3 charta_runtime.py inspect program.cht
   ```
5. Export to charta/python/mq5:
   ```bash
   python3 charta_runtime.py export program.cht charta
   python3 charta_runtime.py export program.cht python
   python3 charta_runtime.py export program.cht mq5
   ```
   - `charta` output must be pure Devanagari and translate `EKSEKUSI_DUAL_ENTRY`, `STRATEGI_AUTO_RBT`, `DI_METATRADER5`, `KE_EMAIL_PEMBUAT`.
   - `python` and `mq5` outputs may contain the original SPOK tokens in comments.
6. Verify `program.cht` permissions `0o600` and JSON envelope with `ciphertext` and `nonce`.
7. Test `ChartaLocalVault` and `ChartaSPOKCompiler` roundtrips in a short Python script; path traversal attempts (e.g. `../../../etc/passwd`, `foo/bar`, `..\windows\system32`) should raise `ValueError`.
8. Run `python3 -m py_compile` on all `.py` files.
9. Grep for hardcoded `CHARTA_MASTER_KEY` values, emails, and credential literals in `.py` source.

## Known gotchas
- `charta_engine.py` creates a default vault directory using `CHARTA_VAULT_PATH` (or `C:\ChartaVault`) at import time.
- `charta_runtime.py` `pack()` chmods output files to `0o600`; `charta_engine.py` and `charta_core_app.py` do the same for `.chrt` files.
- Devanagari rendering requires a Devanagari-capable terminal font; evidence can be validated with `python3` string checks if the font is missing.
