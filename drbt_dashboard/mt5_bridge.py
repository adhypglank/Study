"""MT5 Bridge API — jalankan di mesin Windows yang sama dengan terminal MT5.

Menyediakan data kinerja multi-bot (per magic number) untuk dashboard.
Jalankan:  python mt5_bridge.py   (port 5000)
Expose ke luar dengan cloudflared/ngrok bila dashboard berjalan di mesin lain.
"""
import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify
import MetaTrader5 as mt5

app = Flask(__name__)

SYMBOL = os.environ.get("BRIDGE_SYMBOL", "XAUUSD")
HISTORY_DAYS = int(os.environ.get("BRIDGE_HISTORY_DAYS", "30"))

# Magic number -> nama bot (lihat AUTO_RBT_STATUS.md)
ENGINES = {
    0: "Manual",
    101: "Auto_RBT_V1_SuperSpeed", 102: "Auto_RBT_V1_SuperSpeed",
    201: "Auto_RBT_V2_HyperSonic", 202: "Auto_RBT_V2_HyperSonic",
    301: "Auto_RBT_V2_HyperAgressive", 302: "Auto_RBT_V2_HyperAgressive",
    202604: "Auto_RBT_V1.1_Live",
}


def ensure_mt5():
    if mt5.terminal_info() is None and not mt5.initialize():
        raise ConnectionError(f"MT5 tidak tersedia: {mt5.last_error()}")


@app.route("/api/overview")
def overview():
    ensure_mt5()
    acc = mt5.account_info()
    tick = mt5.symbol_info_tick(SYMBOL)

    positions = mt5.positions_get() or []
    open_by_bot = {}
    for p in positions:
        bot = ENGINES.get(p.magic, f"magic_{p.magic}")
        entry = open_by_bot.setdefault(bot, {"floating": 0.0, "positions": []})
        net = p.profit + getattr(p, "commission", 0.0) + p.swap
        entry["floating"] += net
        entry["positions"].append({
            "ticket": p.ticket, "symbol": p.symbol,
            "type": "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
            "lot": p.volume, "open_price": p.price_open,
            "open_time": p.time, "net_profit": round(net, 2),
        })

    frm = datetime.now(timezone.utc) - timedelta(days=HISTORY_DAYS)
    deals = mt5.history_deals_get(frm, datetime.now(timezone.utc)) or []
    closed = []
    for d in deals:
        if d.entry != mt5.DEAL_ENTRY_OUT:
            continue
        closed.append({
            "time": d.time, "magic": d.magic,
            "bot": ENGINES.get(d.magic, f"magic_{d.magic}"),
            "symbol": d.symbol, "volume": d.volume,
            "net_profit": round(d.profit + d.commission + d.swap, 2),
        })

    return jsonify({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "account": None if acc is None else {
            "login": acc.login, "server": acc.server, "currency": acc.currency,
            "balance": acc.balance, "equity": acc.equity, "margin": acc.margin,
        },
        "tick": None if tick is None else {"symbol": SYMBOL, "bid": tick.bid, "ask": tick.ask},
        "open_by_bot": open_by_bot,
        "closed_deals": closed,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("BRIDGE_PORT", "5000")))
