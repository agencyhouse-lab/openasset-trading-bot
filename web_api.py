#!/usr/bin/env python3
"""
OpenAsset Web API — Admin Dashboard Backend
============================================

Reads from the Telegram bot's JSON databases (no separate DB needed).
Serves the web admin dashboard at / and a REST API at /api/*.

Start: python3 web_api.py
URL:   http://72.62.254.237:8080

Admin password is set via env var OPENASSET_WEB_PASSWORD (default shown below).
"""

import json
import os
import time
import hashlib
import secrets
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Header, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("Install: pip install fastapi uvicorn")
    raise

# ─── Config ──────────────────────────────────────────────────────────────────
DB = Path("/root/openasset_club/telegram_bot/database")
HTML = Path("/root/openasset-trading-bot/web_admin.html")
WEB_PASSWORD = os.environ.get("OPENASSET_WEB_PASSWORD", "openasset2026")
PORT = int(os.environ.get("OPENASSET_WEB_PORT", 8080))

# In-memory session store (key → expiry timestamp)
_sessions: dict = {}
SESSION_TTL = 60 * 60 * 12  # 12 hours

app = FastAPI(title="OpenAsset Admin", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


# ─── DB helpers ──────────────────────────────────────────────────────────────
def _load(name: str) -> dict:
    try:
        p = DB / f"{name}.json"
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return {}


def _load_oa() -> dict:
    try:
        p = DB / "openasset_accounts.json"
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return {}


# ─── Auth ────────────────────────────────────────────────────────────────────
def _valid_session(token: Optional[str]) -> bool:
    if not token:
        return False
    exp = _sessions.get(token, 0)
    if time.time() > exp:
        _sessions.pop(token, None)
        return False
    return True


def _require_auth(x_token: Optional[str] = Header(None)):
    if not _valid_session(x_token):
        raise HTTPException(status_code=401, detail="Unauthorized")


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if HTML.exists():
        return HTMLResponse(HTML.read_text())
    return HTMLResponse("<h1>web_admin.html not found</h1>")


@app.post("/api/login")
def login(body: dict):
    pw = body.get("password", "")
    if pw == WEB_PASSWORD:
        token = secrets.token_hex(24)
        _sessions[token] = time.time() + SESSION_TTL
        return {"token": token}
    raise HTTPException(status_code=401, detail="Wrong password")


@app.post("/api/logout")
def logout(x_token: Optional[str] = Header(None)):
    _sessions.pop(x_token, None)
    return {"ok": True}


@app.get("/api/stats")
def get_stats(x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    users = _load("users")
    subs = _load("subscriptions")
    payments = _load("payments")
    trades = _load("trades")
    accounts = _load("accounts")

    now = datetime.now(timezone.utc)
    active_subs = sum(
        1 for uid, s in subs.items()
        if s.get("status") == "active" and
        datetime.fromisoformat(s.get("expiry", "2000-01-01").replace("Z", "+00:00")) > now
    )
    total_revenue = sum(
        float(p.get("amount", 0)) for p in payments.values()
        if p.get("status") == "confirmed"
    )
    mtd_revenue = sum(
        float(p.get("amount", 0)) for p in payments.values()
        if p.get("status") == "confirmed" and
        p.get("confirmed_at", "")[:7] == now.strftime("%Y-%m")
    )
    live_trades = sum(1 for t in trades.values() if t.get("status") == "OPEN")
    binance_connected = sum(
        1 for u in accounts.values()
        if isinstance(u, dict) and u.get("binance", {}).get("status") == "connected"
    )
    alpaca_connected = sum(
        1 for u in accounts.values()
        if isinstance(u, dict) and u.get("alpaca", {}).get("status") == "connected"
    )

    return {
        "total_users": len(users),
        "active_subscribers": active_subs,
        "total_trades": len(trades),
        "open_trades": live_trades,
        "total_revenue_usd": round(total_revenue, 2),
        "mtd_revenue_usd": round(mtd_revenue, 2),
        "binance_users": binance_connected,
        "alpaca_users": alpaca_connected,
    }


@app.get("/api/users")
def get_users(x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    users = _load("users")
    subs = _load("subscriptions")
    accounts = _load("accounts")
    now = datetime.now(timezone.utc)
    rows = []
    for uid, u in users.items():
        s = subs.get(uid, {})
        acct = accounts.get(uid, {})
        expiry_str = s.get("expiry", "")
        try:
            expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            days_left = (expiry - now).days
            is_active = expiry > now and s.get("status") == "active"
        except Exception:
            days_left = -1
            is_active = False
        platforms = []
        if isinstance(acct, dict):
            for p in ["binance", "alpaca", "oanda"]:
                if acct.get(p, {}).get("status") == "connected":
                    platforms.append(p)
        rows.append({
            "uid": uid,
            "username": u.get("username", "—"),
            "first_name": u.get("first_name", ""),
            "plan": s.get("plan", "none"),
            "active": is_active,
            "days_left": max(days_left, 0),
            "expiry": expiry_str[:10] if expiry_str else "—",
            "joined": u.get("joined_at", "")[:10],
            "platforms": platforms,
        })
    rows.sort(key=lambda x: x["joined"], reverse=True)
    return {"users": rows, "total": len(rows)}


@app.get("/api/trades")
def get_trades(limit: int = 50, x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    trades = _load("trades")
    rows = []
    for tid, t in trades.items():
        rows.append({
            "trade_id": tid,
            "uid": str(t.get("user_id", "")),
            "symbol": t.get("symbol", ""),
            "side": t.get("side", ""),
            "mode": t.get("mode", "PAPER"),
            "status": t.get("status", ""),
            "pnl": round(float(t.get("pnl", 0)), 2),
            "qty": t.get("qty", 0),
            "entry_price": t.get("entry_price", 0),
            "created_at": t.get("created_at", "")[:19],
        })
    rows.sort(key=lambda x: x["created_at"], reverse=True)
    return {"trades": rows[:limit], "total": len(rows)}


@app.get("/api/strategy-lab")
def get_strategy_lab(x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    oa = _load_oa()
    rows = []
    for uid, a in oa.items():
        cash = float(a.get("cash", 0))
        start = float(a.get("starting_cash", 10000))
        trades = a.get("trades", [])
        wins = sum(1 for t in trades if float(t.get("pnl", 0)) >= 0)
        total_pnl = sum(float(t.get("pnl", 0)) for t in trades)
        pos_count = len(a.get("positions", {}))
        rows.append({
            "uid": uid,
            "cash": round(cash, 2),
            "starting_cash": start,
            "total_return_pct": round((cash - start) / start * 100, 1) if start else 0,
            "open_positions": pos_count,
            "total_trades": len(trades),
            "win_rate": round(wins / len(trades) * 100, 1) if trades else 0,
            "total_pnl": round(total_pnl, 2),
        })
    rows.sort(key=lambda x: x["total_pnl"], reverse=True)
    return {"accounts": rows, "total": len(rows)}


@app.get("/api/health")
def get_health(x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    # Check if bot process is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "main.py"],
            capture_output=True, text=True, timeout=3
        )
        bot_running = result.returncode == 0
    except Exception:
        bot_running = False

    # Check log for last activity
    try:
        log = Path("/root/openasset_club/telegram_bot/logs/user_bot.log")
        last_lines = log.read_text().splitlines()[-5:] if log.exists() else []
    except Exception:
        last_lines = []

    return {
        "bot_online": bot_running,
        "last_log_lines": last_lines,
        "db_files": {
            name: (DB / f"{name}.json").exists()
            for name in ["users", "subscriptions", "payments", "trades",
                         "accounts", "openasset_accounts"]
        },
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/revenue")
def get_revenue(x_token: Optional[str] = Header(None)):
    _require_auth(x_token)
    payments = _load("payments")
    # Group by month
    monthly: dict = {}
    for p in payments.values():
        if p.get("status") != "confirmed":
            continue
        month = p.get("confirmed_at", "")[:7]
        if not month:
            continue
        monthly[month] = monthly.get(month, 0) + float(p.get("amount", 0))
    # Last 6 months sorted
    months = sorted(monthly.keys())[-6:]
    return {
        "monthly": [{"month": m, "revenue": round(monthly[m], 2)} for m in months],
        "total": round(sum(monthly.values()), 2),
    }


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"""
╔════════════════════════════════════╗
║  OpenAsset Web Dashboard           ║
╠════════════════════════════════════╣
║  URL:      http://72.62.254.237:{PORT}  ║
║  Password: {WEB_PASSWORD:<26} ║
║  Stop:     Ctrl+C                  ║
╚════════════════════════════════════╝
""")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
