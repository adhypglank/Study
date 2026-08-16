"""ZeroMQ-style HTTP bridge between MetaTrader 5 and encrypted Charta .cht packages.

Run this helper before launching MetaTrader 5:

    CHARTA_MASTER_KEY=... CHARTA_VAULT_PATH=./vault python3 charta_mt5_bridge.py

Then in MetaTrader 5 attach the .mq5 generated with:

    python3 charta_runtime.py export program.cht mq5

and add `http://127.0.0.1:15555` to the terminal's allowed URL list.
"""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from charta_runtime import unpack, _key, FORMAT


HOST = os.environ.get("CHARTA_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("CHARTA_BRIDGE_PORT", "15555"))
VAULT_PATH = Path(os.environ.get("CHARTA_VAULT_PATH", "."))


class ChartaSignalSource:
    """Decrypt a .cht file once and serve its instructions sequentially."""

    def __init__(self, package: Path):
        self.module = unpack(package)
        self.index = 0
        self.signals: list[dict] = []
        for idx, item in enumerate(self.module.instructions, 1):
            if item.op == "spok":
                data = item.data
                ctx = " ".join(data.get("context", []))
                self.signals.append({
                    "id": f"AG{idx}",
                    "spok": f"{data['subject']} {data['predicate']} {data['object']}{' ' + ctx if ctx else ''}",
                })

    def current(self) -> dict:
        if not self.signals:
            return {"id": "", "spok": "", "done": True}
        if self.index >= len(self.signals):
            return {"id": "", "spok": "", "done": True, "module": self.module.name}
        sig = dict(self.signals[self.index])
        sig["done"] = False
        sig["module"] = self.module.name
        return sig

    def ack(self, signal_id: str) -> bool:
        if not self.signals:
            return False
        current = self.signals[self.index]
        if current["id"] == signal_id:
            self.index = min(self.index + 1, len(self.signals))
            return True
        return False


def _load_first_chrt_or_cht() -> ChartaSignalSource:
    candidates = sorted(VAULT_PATH.glob("*.cht")) + sorted(VAULT_PATH.glob("*.chrt"))
    if not candidates:
        raise RuntimeError(f"No .cht or .chrt package found in {VAULT_PATH}")
    return ChartaSignalSource(candidates[0])


class _Handler(BaseHTTPRequestHandler):
    source: ChartaSignalSource | None = None

    def log_message(self, fmt: str, *args) -> None:
        print(f"[CHARTA BRIDGE] {self.address_string()} - {fmt % args}")

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _load(self) -> ChartaSignalSource:
        if _Handler.source is None:
            _Handler.source = _load_first_chrt_or_cht()
        return _Handler.source

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/signal":
            try:
                self._json(200, self._load().current())
            except Exception as exc:
                self._json(500, {"error": str(exc)})
        else:
            self._json(404, {"error": "unknown endpoint"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/ack":
            try:
                source = self._load()
                sid = qs.get("id", [""])[0]
                ok = source.ack(sid)
                self._json(200, {"ack": ok, "next": source.current()})
            except Exception as exc:
                self._json(500, {"error": str(exc)})
        else:
            self._json(404, {"error": "unknown endpoint"})


def main() -> None:
    _key()  # verify key exists at startup
    server = HTTPServer((HOST, PORT), _Handler)
    print(f"[CHARTA BRIDGE] serving Charta signals for MT5 at http://{HOST}:{PORT}")
    print(f"[CHARTA BRIDGE] vault: {VAULT_PATH.absolute()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[CHARTA BRIDGE] stopped.")


if __name__ == "__main__":
    main()
