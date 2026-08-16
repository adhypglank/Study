"""Charta protective wrapper (anti-plagiarism / anti-theft) for existing files.

This tool wraps an existing source/binary file into an encrypted `.chrt`
package.  Without the correct ``CHARTA_MASTER_KEY`` the content cannot be
copied, viewed, or executed as the original program.  On tamper attempts the
output is zeroed and a tamper event is returned; it deliberately does NOT
cause system restarts or any other denial-of-service side-effect.

Usage:
    CHARTA_MASTER_KEY=... python3 charta_protect.py wrap secret.py secret.py.chrt
    CHARTA_MASTER_KEY=... python3 charta_protect.py unwrap secret.py.chrt secret_restored.py
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import json
import os
import secrets
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise RuntimeError("Install package 'cryptography' to use Charta protect.") from exc


KEY_ENV = "CHARTA_MASTER_KEY"
OWNER_ENV = "CHARTA_OWNER"
FORMAT = "CHRT-PROTECT-1"


def _key() -> bytes:
    encoded = os.environ.get(KEY_ENV)
    if not encoded:
        raise RuntimeError(
            f"Set {KEY_ENV} to a base64-urlsafe 32-byte key. "
            "Generate one with: python3 -c \"import base64, secrets; "
            "print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\""
        )
    try:
        key = base64.urlsafe_b64decode(encoded.encode("ascii"))
    except Exception as exc:
        raise RuntimeError(f"Invalid {KEY_ENV} value") from exc
    if len(key) != 32:
        raise RuntimeError(f"{KEY_ENV} must decode to exactly 32 bytes")
    return key


def _watermark(filename: str) -> dict:
    return {
        "format": FORMAT,
        "filename": filename,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "owner": os.environ.get(OWNER_ENV, "Adi Putra (Adhyp Glank)"),
    }


def wrap(input_path: Path, output_path: Path) -> None:
    """Encrypt a file and append a visible decoy header that hides its true size."""
    plaintext = input_path.read_bytes()
    digest = hashlib.sha256(plaintext).hexdigest()
    manifest = _watermark(input_path.name)
    manifest["sha256"] = digest

    nonce = secrets.token_bytes(12)
    associated_data = json.dumps(manifest, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ciphertext = AESGCM(_key()).encrypt(nonce, plaintext, associated_data)

    envelope = {
        "format": FORMAT,
        "manifest": manifest,
        "nonce": base64.urlsafe_b64encode(nonce).decode("ascii"),
        "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
        "associated": base64.urlsafe_b64encode(associated_data).decode("ascii"),
    }

    inner = base64.urlsafe_b64encode(json.dumps(envelope, separators=(",", ":")).encode("utf-8")).decode("ascii")
    # Decoy header: the file starts with a benign tag and ends with a footer.
    # Without the key the bytes between look like random base64 and cannot be interpreted.
    wrapped = f"CHRT_PROTECT_V1::{inner}::CHRT_PROTECT_END".encode("ascii")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(wrapped)
    os.chmod(output_path, 0o600)
    print(f"[CHARTA PROTECT] Wrapped {input_path} -> {output_path}")
    print(f"[CHARTA PROTECT] Owner: {manifest['owner']} | SHA256: {digest[:16]}...")


def unwrap(input_path: Path, output_path: Path) -> None:
    """Decrypt a protected file. Wrong key yields tamper-evident zero-length output."""
    raw = input_path.read_bytes()
    try:
        text = raw.decode("ascii")
        parts = text.split("::", 2)
        if len(parts) != 3 or parts[0] != "CHRT_PROTECT_V1" or parts[2] != "CHRT_PROTECT_END":
            raise ValueError("Not a Charta protect file")
        envelope = json.loads(base64.urlsafe_b64decode(parts[1]).decode("utf-8"))
    except Exception as exc:
        output_path.write_bytes(b"")
        raise RuntimeError("[SECURITY BREACH] File structure is not a valid Charta protect envelope.") from exc

    if envelope.get("format") != FORMAT:
        output_path.write_bytes(b"")
        raise RuntimeError("[SECURITY BREACH] Unsupported protect format.")

    nonce = base64.urlsafe_b64decode(envelope["nonce"].encode("ascii"))
    ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
    associated_data = base64.urlsafe_b64decode(envelope["associated"].encode("ascii"))
    manifest = json.loads(associated_data.decode("utf-8"))

    try:
        plaintext = AESGCM(_key()).decrypt(nonce, ciphertext, associated_data)
    except Exception as exc:
        # Tamper attempt: produce empty/undecodable output, do NOT modify the system.
        output_path.write_bytes(b"")
        print("[CHARTA PROTECT] Kunci salah atau file telah dirusak. Output dikosongkan.")
        raise RuntimeError("[CHARTA PROTECT] Invalid key / tampered file. Output zeroed.") from exc

    digest = hashlib.sha256(plaintext).hexdigest()
    if manifest.get("sha256") and manifest["sha256"] != digest:
        output_path.write_bytes(b"")
        raise RuntimeError("[SECURITY BREACH] SHA256 mismatch after decryption.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(plaintext)
    print(f"[CHARTA PROTECT] Unwrapped {input_path} -> {output_path}")
    print(f"[CHARTA PROTECT] Watermark owner: {manifest.get('owner')}")


def peek(input_path: Path) -> tuple[dict, bytes]:
    """Decrypt a protected file and return its (manifest, plaintext) without writing it."""
    raw = input_path.read_bytes()
    text = raw.decode("ascii")
    parts = text.split("::", 2)
    if len(parts) != 3 or parts[0] != "CHRT_PROTECT_V1" or parts[2] != "CHRT_PROTECT_END":
        raise ValueError("Not a Charta protect file")
    envelope = json.loads(base64.urlsafe_b64decode(parts[1]).decode("utf-8"))
    if envelope.get("format") != FORMAT:
        raise ValueError("Unsupported protect format")

    nonce = base64.urlsafe_b64decode(envelope["nonce"].encode("ascii"))
    ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
    associated = base64.urlsafe_b64decode(envelope["associated"].encode("ascii"))
    manifest = json.loads(associated.decode("utf-8"))

    try:
        plaintext = AESGCM(_key()).decrypt(nonce, ciphertext, associated)
    except Exception as exc:
        raise RuntimeError("[CHARTA PROTECT] Invalid key or tampered file.") from exc

    digest = hashlib.sha256(plaintext).hexdigest()
    if manifest.get("sha256") and manifest["sha256"] != digest:
        raise RuntimeError("[SECURITY BREACH] SHA256 mismatch after decryption.")

    return manifest, plaintext


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrap/unwrap Charta protected files")
    sub = parser.add_subparsers(dest="command", required=True)

    wrap_parser = sub.add_parser("wrap", help="Wrap a file into an encrypted .chrt")
    wrap_parser.add_argument("input", type=Path)
    wrap_parser.add_argument("output", type=Path)
    wrap_parser.set_defaults(action=lambda args: wrap(args.input, args.output))

    unwrap_parser = sub.add_parser("unwrap", help="Restore a .chrt to the original file")
    unwrap_parser.add_argument("input", type=Path)
    unwrap_parser.add_argument("output", type=Path)
    unwrap_parser.set_defaults(action=lambda args: unwrap(args.input, args.output))

    args = parser.parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
