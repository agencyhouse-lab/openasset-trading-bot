#!/usr/bin/env python3
"""
OpenAsset Internal — Paper Trading Engine
==========================================

Self-contained paper trading engine. Zero broker dependency.

  * Per-user accounts (JSON persisted)
  * $10,000 starting balance
  * Long-only positions (Phase 1)
  * Market orders by dollar amount (notional)
  * Stop-loss + take-profit with REAL auto-close (background monitor)
  * Supports every symbol in openasset_feeds (40+ across 6 asset classes)

Safety rails:
  * Max $1,000 per single trade (paper sandbox is generous vs live's $50)
  * Symbol must exist in feeds registry
  * Insufficient cash check
  * No leverage / no shorts in Phase 1

Public surface (also serves as the "SDK" for the future REST API):
    place_market_buy(uid, symbol, usd_amount)  -> dict
    close_position(uid, symbol)                -> dict
    set_sl_tp(uid, symbol, sl_pct, tp_pct)     -> dict
    get_cash(uid)                              -> float
    get_positions(uid)                         -> dict
    get_portfolio_value(uid)                   -> float
    get_trades(uid, limit=20)                  -> list
    reset_account(uid)                         -> dict
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timezone
from typing import Optional, Dict, List

from openasset_feeds import get_price, get_symbol_info, asset_class_of

logger = logging.getLogger(__name__)

DB_PATH = "/root/openasset_club/telegram_bot/database"
ACCOUNTS_FILE = "openasset_accounts"

STARTING_CASH = 10_000.00
MAX_USD_PER_TRADE = 1_000.00
MIN_USD_PER_TRADE = 1.00

_LOCK = threading.RLock()  # protects JSON read/modify/write


# ─── DB helpers ──────────────────────────────────────────────────────────────
def _load() -> dict:
    try:
        with open(f"{DB_PATH}/{ACCOUNTS_FILE}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    os.makedirs(DB_PATH, exist_ok=True)
    tmp = f"{DB_PATH}/{ACCOUNTS_FILE}.json.tmp"
    final = f"{DB_PATH}/{ACCOUNTS_FILE}.json"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, final)  # atomic write


def _new_account() -> dict:
    return {
        "starting_cash": STARTING_CASH,
        "cash":          STARTING_CASH,
        "positions":     {},   # symbol → {qty, avg_entry, side, opened_at}
        "stops":         {},   # symbol → {stop_loss, take_profit, entry, sl_pct, tp_pct}
        "trades":        [],   # closed-trade history
        "orders":        [],   # all order events
        "created_at":    datetime.now(timezone.utc).isoformat(),
    }


def get_or_create_account(uid: str) -> dict:
    with _LOCK:
        data = _load()
        if str(uid) not in data:
            data[str(uid)] = _new_account()
            _save(data)
        return data[str(uid)]


# ─── Read API ────────────────────────────────────────────────────────────────
def get_cash(uid: str) -> float:
    return get_or_create_account(uid)["cash"]


def get_positions(uid: str) -> Dict[str, dict]:
    return get_or_create_account(uid).get("positions", {})


def get_position(uid: str, symbol: str) -> Optional[dict]:
    return get_positions(uid).get(symbol.upper())


def get_portfolio_value(uid: str) -> float:
    """Cash + mark-to-market value of all positions."""
    a = get_or_create_account(uid)
    value = a["cash"]
    for sym, pos in a.get("positions", {}).items():
        p = get_price(sym)
        if p > 0:
            value += pos["qty"] * p
    return value


def get_unrealized_pnl(uid: str) -> float:
    a = get_or_create_account(uid)
    pnl = 0.0
    for sym, pos in a.get("positions", {}).items():
        p = get_price(sym)
        if p > 0:
            pnl += (p - pos["avg_entry"]) * pos["qty"]
    return pnl


def get_trades(uid: str, limit: int = 20) -> List[dict]:
    return get_or_create_account(uid).get("trades", [])[-limit:][::-1]


# ─── Write API ───────────────────────────────────────────────────────────────
def place_market_buy(uid: str, symbol: str, usd_amount: float) -> dict:
    """
    Market BUY for a dollar amount (notional).
    Returns dict with success/error. On success includes order_id, qty, fill_price.
    """
    symbol = symbol.upper()
    cls = asset_class_of(symbol)
    if not cls:
        return {"success": False, "error": f"Symbol {symbol} not supported"}

    if usd_amount > MAX_USD_PER_TRADE:
        return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
    if usd_amount < MIN_USD_PER_TRADE:
        return {"success": False, "error": f"Min order ${MIN_USD_PER_TRADE}"}

    price = get_price(symbol)
    if price <= 0:
        return {"success": False, "error": f"Price feed unavailable for {symbol}"}

    with _LOCK:
        data = _load()
        if str(uid) not in data:
            data[str(uid)] = _new_account()
        a = data[str(uid)]

        if a["cash"] < usd_amount:
            return {"success": False,
                    "error": f"Insufficient cash: have ${a['cash']:.2f}, need ${usd_amount:.2f}"}

        qty = usd_amount / price
        a["cash"] -= usd_amount

        # Merge into existing position (avg entry)
        pos = a["positions"].get(symbol)
        if pos:
            total_qty = pos["qty"] + qty
            a["positions"][symbol] = {
                "qty":       total_qty,
                "avg_entry": (pos["avg_entry"] * pos["qty"] + price * qty) / total_qty,
                "side":      "long",
                "opened_at": pos.get("opened_at",
                                     datetime.now(timezone.utc).isoformat()),
            }
        else:
            a["positions"][symbol] = {
                "qty":       qty,
                "avg_entry": price,
                "side":      "long",
                "opened_at": datetime.now(timezone.utc).isoformat(),
            }

        order_id = f"OA_{int(time.time() * 1000)}_{uid}"
        order = {
            "order_id":  order_id,
            "symbol":    symbol,
            "side":      "BUY",
            "qty":       qty,
            "price":     price,
            "usd":       usd_amount,
            "type":      "MARKET",
            "ts":        datetime.now(timezone.utc).isoformat(),
        }
        a.setdefault("orders", []).append(order)
        _save(data)

    return {
        "success":     True,
        "order_id":    order_id,
        "symbol":      symbol,
        "qty":         qty,
        "fill_price":  price,
        "usd_spent":   usd_amount,
        "asset_class": cls,
    }


def close_position(uid: str, symbol: str, reason: str = "MANUAL") -> dict:
    symbol = symbol.upper()
    price = get_price(symbol)
    if price <= 0:
        return {"success": False, "error": f"Price feed unavailable for {symbol}"}

    with _LOCK:
        data = _load()
        a = data.get(str(uid))
        if not a:
            return {"success": False, "error": "Account not found"}
        pos = a.get("positions", {}).get(symbol)
        if not pos:
            return {"success": False, "error": f"No open position in {symbol}"}

        qty = pos["qty"]
        proceeds = qty * price
        pnl = (price - pos["avg_entry"]) * qty
        a["cash"] += proceeds

        trade = {
            "symbol":   symbol,
            "side":     "SELL",
            "reason":   reason,  # MANUAL | SL_HIT | TP_HIT
            "qty":      qty,
            "entry":    pos["avg_entry"],
            "exit":     price,
            "pnl":      pnl,
            "pnl_pct":  ((price - pos["avg_entry"]) / pos["avg_entry"] * 100)
                        if pos["avg_entry"] else 0,
            "ts":       datetime.now(timezone.utc).isoformat(),
        }
        a.setdefault("trades", []).append(trade)
        del a["positions"][symbol]
        a.get("stops", {}).pop(symbol, None)
        _save(data)

    return {
        "success":    True,
        "symbol":     symbol,
        "qty":        qty,
        "fill_price": price,
        "pnl":        pnl,
        "proceeds":   proceeds,
        "reason":     reason,
    }


def set_sl_tp(uid: str, symbol: str,
              sl_pct: float = 0.5, tp_pct: float = 3.0) -> dict:
    """
    Attach stop-loss and take-profit (%) to an open long position.
    Background monitor will close the position when price hits either.
    """
    symbol = symbol.upper()
    with _LOCK:
        data = _load()
        a = data.get(str(uid))
        if not a:
            return {"success": False, "error": "Account not found"}
        pos = a.get("positions", {}).get(symbol)
        if not pos:
            return {"success": False, "error": f"No position in {symbol}"}

        entry = pos["avg_entry"]
        sl_price = entry * (1 - sl_pct / 100)
        tp_price = entry * (1 + tp_pct / 100)
        a.setdefault("stops", {})[symbol] = {
            "stop_loss":   sl_price,
            "take_profit": tp_price,
            "entry":       entry,
            "sl_pct":      sl_pct,
            "tp_pct":      tp_pct,
        }
        _save(data)
    return {
        "success":     True,
        "stop_loss":   sl_price,
        "take_profit": tp_price,
        "sl_pct":      sl_pct,
        "tp_pct":      tp_pct,
    }


def reset_account(uid: str) -> dict:
    with _LOCK:
        data = _load()
        data[str(uid)] = _new_account()
        _save(data)
    return {"success": True, "starting_cash": STARTING_CASH}


# ─── Background SL/TP monitor ────────────────────────────────────────────────
_monitor_thread: Optional[threading.Thread] = None
_monitor_stop = threading.Event()
MONITOR_INTERVAL = 30  # seconds


def _monitor_loop():
    logger.info("OpenAsset SL/TP monitor: started")
    while not _monitor_stop.is_set():
        try:
            with _LOCK:
                data = _load()
            changed = False
            for uid, a in data.items():
                stops = a.get("stops", {})
                if not stops:
                    continue
                for symbol in list(stops.keys()):
                    pos = a.get("positions", {}).get(symbol)
                    if not pos:
                        # orphan stop — clean up
                        del stops[symbol]
                        changed = True
                        continue
                    p = get_price(symbol)
                    if p <= 0:
                        continue
                    lv = stops[symbol]
                    hit_sl = p <= lv["stop_loss"]
                    hit_tp = p >= lv["take_profit"]
                    if hit_sl or hit_tp:
                        reason = "SL_HIT" if hit_sl else "TP_HIT"
                        qty = pos["qty"]
                        pnl = (p - pos["avg_entry"]) * qty
                        a["cash"] += qty * p
                        a.setdefault("trades", []).append({
                            "symbol":  symbol,
                            "side":    "AUTO_CLOSE",
                            "reason":  reason,
                            "qty":     qty,
                            "entry":   pos["avg_entry"],
                            "exit":    p,
                            "pnl":     pnl,
                            "pnl_pct": ((p - pos["avg_entry"])
                                        / pos["avg_entry"] * 100)
                                       if pos["avg_entry"] else 0,
                            "ts":      datetime.now(timezone.utc).isoformat(),
                        })
                        del a["positions"][symbol]
                        del stops[symbol]
                        changed = True
                        logger.info(
                            f"AUTO-CLOSE {symbol} for uid={uid}: "
                            f"{reason} @ {p:.4f}, PnL=${pnl:.2f}"
                        )
            if changed:
                with _LOCK:
                    _save(data)
        except Exception as e:
            logger.error(f"monitor loop error: {e}", exc_info=True)
        _monitor_stop.wait(MONITOR_INTERVAL)


def start_monitor() -> bool:
    """Start the SL/TP background monitor. Idempotent. Returns True if newly started."""
    global _monitor_thread
    if _monitor_thread and _monitor_thread.is_alive():
        return False
    _monitor_stop.clear()
    _monitor_thread = threading.Thread(
        target=_monitor_loop, daemon=True, name="oa_sltp_monitor"
    )
    _monitor_thread.start()
    return True


def stop_monitor():
    _monitor_stop.set()


# Auto-start on import (runs in daemon thread — safe)
start_monitor()
