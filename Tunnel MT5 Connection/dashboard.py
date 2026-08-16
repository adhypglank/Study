"""Dashboard Visualisasi Kinerja Multi-Bot dRBT.

Sumber data: MT5 Bridge API (mt5_bridge.py) via env BRIDGE_URL,
atau mode demo dengan data simulasi: DEMO=1.

Jalankan:  BRIDGE_URL=https://<tunnel>/api/overview python dashboard.py
Demo:      DEMO=1 python dashboard.py
"""
import os
import random
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

BRIDGE_URL = os.environ.get("BRIDGE_URL", "http://localhost:5000/api/overview")
DEMO = os.environ.get("DEMO", "0") == "1"

DEMO_BOTS = ["Auto_RBT_V1_SuperSpeed", "Auto_RBT_V2_HyperSonic", "Auto_RBT_V2_HyperAgressive"]


def demo_overview():
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    closed = []
    for bot_index, bot in enumerate(DEMO_BOTS):
        edge = [0.4, 0.1, -0.2][bot_index]
        for day in range(30):
            for _ in range(rng.randint(2, 6)):
                closed.append({
                    "time": int((now - timedelta(days=29 - day, minutes=rng.randint(0, 600))).timestamp()),
                    "bot": bot, "symbol": "XAUUSD",
                    "volume": 0.01,
                    "net_profit": round(rng.gauss(edge, 3.5), 2),
                })
    closed.sort(key=lambda d: d["time"])
    open_by_bot = {}
    for bot in DEMO_BOTS:
        positions = []
        floating = 0.0
        for _ in range(rng.randint(1, 3)):
            net = round(rng.gauss(0, 4), 2)
            floating += net
            positions.append({
                "ticket": rng.randint(10_000_000, 99_999_999), "symbol": "XAUUSD",
                "type": rng.choice(["BUY", "SELL"]), "lot": 0.01,
                "open_price": round(2400 + rng.uniform(-30, 30), 2),
                "open_time": int(now.timestamp()) - rng.randint(600, 20000),
                "net_profit": net,
            })
        open_by_bot[bot] = {"floating": round(floating, 2), "positions": positions}
    return {
        "generated_at": now.isoformat(),
        "account": {"login": 12345678, "server": "Demo-Server", "currency": "USD",
                    "balance": 10_000.0, "equity": 10_000.0 + sum(b["floating"] for b in open_by_bot.values()),
                    "margin": 120.0},
        "tick": {"symbol": "XAUUSD", "bid": 2401.25, "ask": 2401.55},
        "open_by_bot": open_by_bot,
        "closed_deals": closed,
    }


def fetch_overview():
    if DEMO:
        return demo_overview()
    resp = requests.get(BRIDGE_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_stats(overview):
    per_bot = defaultdict(lambda: {"trades": 0, "wins": 0, "net": 0.0, "curve_t": [], "curve_v": []})
    cumulative = defaultdict(float)
    for deal in overview.get("closed_deals", []):
        bot = deal["bot"]
        stats = per_bot[bot]
        stats["trades"] += 1
        if deal["net_profit"] > 0:
            stats["wins"] += 1
        stats["net"] += deal["net_profit"]
        cumulative[bot] += deal["net_profit"]
        stats["curve_t"].append(datetime.fromtimestamp(deal["time"], tz=timezone.utc).isoformat())
        stats["curve_v"].append(round(cumulative[bot], 2))
    result = {}
    for bot, stats in per_bot.items():
        result[bot] = {
            "trades": stats["trades"],
            "win_rate": round(100 * stats["wins"] / stats["trades"], 1) if stats["trades"] else 0.0,
            "net_profit": round(stats["net"], 2),
            "curve_t": stats["curve_t"], "curve_v": stats["curve_v"],
        }
    return result


@app.route("/api/dashboard")
def api_dashboard():
    overview = fetch_overview()
    return jsonify({
        "mode": "DEMO" if DEMO else "LIVE",
        "generated_at": overview.get("generated_at"),
        "account": overview.get("account"),
        "tick": overview.get("tick"),
        "open_by_bot": overview.get("open_by_bot", {}),
        "stats": build_stats(overview),
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("DASHBOARD_PORT", "8050")))
