#!/usr/bin/env python3
"""
OpenAsset Trading Dashboard — Live Binance Integration
======================================================

When the user has Binance API connected:
  * Home screen shows REAL USDT balance
  * Market Data shows LIVE prices for BTC/ETH/BNB/SOL
  * Trade Detail shows LIVE price for the selected symbol
  * Manual BUY/SELL in Live Mode places REAL orders (with hard caps)

When the user has NOT connected Binance:
  * Falls back to demo prices
  * Dashboard still works, no crashes

Live Mode is OFF by default. User must explicitly toggle in Settings.
Stocks/ETFs/Commodities stay in demo mode until Alpaca integration.
"""

import os
import json
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

try:
    from binance_client import (
        BinanceClient,
        get_client_for_user,
        get_user_binance_creds,
        is_live_mode,
        set_live_mode,
        calc_trade_size_usd,
        to_binance_symbol,
        MAX_USD_PER_TRADE,
    )
    BINANCE_LOADED = True
except ImportError:
    BINANCE_LOADED = False

logger = logging.getLogger(__name__)

ADMIN_ID = 5587885687
DB_PATH = "/root/openasset_club/telegram_bot/database"

TRADING_CALLBACK_PATTERN = (
    r"^(td_home|td_auto|td_manual|td_market|td_history|"
    r"td_stats|td_settings|mt_|exec_buy_|exec_sell_|"
    r"confirm_buy_|confirm_sell_|bot_start|bot_config|"
    r"settings_notif|settings_verify|settings_toggle_mode|"
    r"settings_confirm_live)"
)

LIVE_SYMBOLS = {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD",
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"}

DEMO_PRICES = {
    "SPY": ("$521.44", "$523.10", "$519.80", "+0.31%", True),
    "QQQ": ("$442.10", "$445.00", "$440.20", "+0.52%", True),
    "GLD": ("$231.75", "$232.50", "$230.80", "+0.18%", True),
    "USO": ("$74.20",  "$75.10",  "$73.80",  "+0.54%", True),
}


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _load(name):
    try:
        with open(f"{DB_PATH}/{name}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(name, data):
    os.makedirs(DB_PATH, exist_ok=True)
    with open(f"{DB_PATH}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)


def ts_now():
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def date_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_user_trades(uid):
    return [t for t in _load("trades").values()
            if str(t.get("user_id")) == str(uid)]


def kb(*rows):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in rows
    ])


def mode_badge(uid):
    if BINANCE_LOADED and is_live_mode(uid):
        return "🔴 *LIVE MODE*"
    return "🧪 *PAPER MODE*"


def fmt_usd(n):
    return f"${n:,.2f}" if abs(n) >= 1 else f"${n:.4f}"


def fmt_pct(n):
    sign = "+" if n >= 0 else ""
    return f"{sign}{n:.2f}%"


# ─── SCREEN 1: Trading Home ──────────────────────────────────────────────────
def screen_trading_home(uid):
    badge = mode_badge(uid)
    has_creds = BINANCE_LOADED and get_user_binance_creds(uid) is not None

    bal_line = "🔗 Connect Binance to see balance"
    if has_creds:
        client = get_client_for_user(uid)
        if client:
            usdt = client.get_balance("USDT")
            bal_line = f"💰 USDT Balance: `{fmt_usd(usdt)}`"

    trades = get_user_trades(uid)
    open_t = [t for t in trades if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Trading Dashboard*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"{bal_line}\n"
        f"📈 Open trades: `{len(open_t)}`\n"
        f"📋 Total:       `{len(trades)} trades`\n\n"
        f"🕐 `{ts_now()}` · `{date_now()}`"
    )
    keyboard = kb(
        [("🤖 Auto Trading", "td_auto"),    ("✏️ Manual Trade", "td_manual")],
        [("📈 Market Data",  "td_market"),  ("📋 Trade History","td_history")],
        [("📊 Statistics",   "td_stats"),   ("⚙️ Bot Settings", "td_settings")],
        [("🏠 Main Menu",    "main_menu")],
    )
    return text, keyboard


# ─── SCREEN 2: Auto Trading ──────────────────────────────────────────────────
def screen_auto(uid):
    binance_ok = BINANCE_LOADED and get_user_binance_creds(uid) is not None
    open_t = [t for t in get_user_trades(uid) if t.get("status") == "OPEN"]
    badge = mode_badge(uid)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Auto Trading Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"Exchange: `{'Binance ✅' if binance_ok else '⚠️ Connect first'}`\n"
        f"Status:   `⬜ Standby`\n"
        f"Open:     `{len(open_t)} positions`\n\n"
        "⚙️ *Default Settings*\n"
        "├ Risk/Trade: `1% of balance`\n"
        f"├ Max/Trade:  `${MAX_USD_PER_TRADE} cap`\n"
        "├ Stop Loss:  `2%`\n"
        "├ Take Profit:`3%`\n"
        "└ Strategy:   `Trend following`\n\n"
        "_Auto engine ships in Phase 4._\n"
        "_For now use Manual Trade._"
    )
    keyboard = kb(
        [("📋 Open Trades", "td_history"), ("📊 Statistics", "td_stats")],
        [("⬅️ Dashboard",   "td_home")],
    )
    return text, keyboard


# ─── SCREEN 3: Manual Trading ────────────────────────────────────────────────
def screen_manual():
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✏️ *Manual Trading*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Live (Binance):*\n"
        "_Real-time prices, real orders in Live Mode._\n\n"
        "*Demo (Stocks/ETFs):*\n"
        "_Paper trading only._\n\n"
        "Choose an asset:"
    )
    keyboard = kb(
        [("₿ BTC/USD",   "mt_BTCUSD"),  ("Ξ ETH/USD",  "mt_ETHUSD")],
        [("🟡 BNB/USD",  "mt_BNBUSD"),  ("◎ SOL/USD",  "mt_SOLUSD")],
        [("📈 SPY",      "mt_SPY"),     ("📈 QQQ",     "mt_QQQ")],
        [("🥇 GLD",      "mt_GLD"),     ("⚫ USO",     "mt_USO")],
        [("⬅️ Dashboard","td_home")],
    )
    return text, keyboard


# ─── SCREEN 4: Trade Detail ──────────────────────────────────────────────────
def screen_trade_detail(symbol, uid):
    badge = mode_badge(uid)
    is_crypto = symbol.upper() in LIVE_SYMBOLS
    has_creds = BINANCE_LOADED and get_user_binance_creds(uid) is not None

    if is_crypto and has_creds:
        client = get_client_for_user(uid)
        if client:
            s = client.get_24h_stats(symbol)
            p, hi, lo = fmt_usd(s["price"]), fmt_usd(s["high"]), fmt_usd(s["low"])
            chg = fmt_pct(s["change_pct"])
            arrow = "✅" if s["change_pct"] >= 0 else "❌"
            data_tag = "🟢 LIVE"
        else:
            p, hi, lo, chg, arrow, data_tag = "—", "—", "—", "—", "⚠️", "ERROR"
    elif is_crypto and not has_creds:
        p, hi, lo, chg, arrow, data_tag = "—", "—", "—", "—", "⚠️", "Connect API"
    else:
        d = DEMO_PRICES.get(symbol, ("—", "—", "—", "—", True))
        p, hi, lo, chg = d[0], d[1], d[2], d[3]
        arrow = "✅" if d[4] else "❌"
        data_tag = "📋 DEMO"

    size_line = ""
    if is_crypto and has_creds:
        client = get_client_for_user(uid)
        if client:
            usdt = client.get_balance("USDT")
            size = calc_trade_size_usd(usdt)
            size_line = f"\n💵 Trade size: `{fmt_usd(size)}` _(1%, capped)_"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{symbol}*  ·  `{data_tag}`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"💲 Price:     `{p}`\n"
        f"⬆️  24h High: `{hi}`\n"
        f"⬇️  24h Low:  `{lo}`\n"
        f"📈 Change:    `{chg}` {arrow}"
        f"{size_line}\n\n"
        "🛡 *Risk Settings*\n"
        "├ Risk:        `1% of balance`\n"
        f"├ Max trade:   `${MAX_USD_PER_TRADE}`\n"
        "├ Stop Loss:   `−2%`\n"
        "└ Take Profit: `+3%`"
    )

    if is_crypto and has_creds:
        keyboard = kb(
            [("🟢 BUY",  f"exec_buy_{symbol}"), ("🔴 SELL", f"exec_sell_{symbol}")],
            [("⬅️ Back", "td_manual")],
        )
    elif is_crypto and not has_creds:
        keyboard = kb(
            [("🔗 Connect Binance first", "main_trading_menu")],
            [("⬅️ Back", "td_manual")],
        )
    else:
        keyboard = kb(
            [("📋 Paper BUY",  f"exec_buy_{symbol}"),
             ("📋 Paper SELL", f"exec_sell_{symbol}")],
            [("⬅️ Back", "td_manual")],
        )
    return text, keyboard


# ─── SCREEN 5: Market Data ───────────────────────────────────────────────────
def screen_market(uid):
    has_creds = BINANCE_LOADED and get_user_binance_creds(uid) is not None

    if has_creds:
        client = get_client_for_user(uid)
        if client:
            try:
                btc = client.get_24h_stats("BTCUSDT")
                eth = client.get_24h_stats("ETHUSDT")
                bnb = client.get_24h_stats("BNBUSDT")
                sol = client.get_24h_stats("SOLUSDT")
                crypto_block = (
                    "🔶 *Crypto* `🟢 LIVE`\n"
                    f"├ ₿  BTC `{fmt_usd(btc['price'])}` `{fmt_pct(btc['change_pct'])}` "
                    f"{'✅' if btc['change_pct']>=0 else '❌'}\n"
                    f"├ Ξ  ETH `{fmt_usd(eth['price'])}` `{fmt_pct(eth['change_pct'])}` "
                    f"{'✅' if eth['change_pct']>=0 else '❌'}\n"
                    f"├ BNB    `{fmt_usd(bnb['price'])}` `{fmt_pct(bnb['change_pct'])}` "
                    f"{'✅' if bnb['change_pct']>=0 else '❌'}\n"
                    f"└ SOL    `{fmt_usd(sol['price'])}` `{fmt_pct(sol['change_pct'])}` "
                    f"{'✅' if sol['change_pct']>=0 else '❌'}\n\n"
                )
            except Exception as e:
                logger.warning(f"Market live fetch failed: {e}")
                crypto_block = "🔶 *Crypto* `⚠️ API ERROR`\n_Check API key._\n\n"
        else:
            crypto_block = "🔶 *Crypto* `⚠️ Init failed`\n\n"
    else:
        crypto_block = (
            "🔶 *Crypto* `🔗 Connect Binance`\n"
            "_Add API key for live data._\n\n"
        )

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 *Market Data*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{crypto_block}"
        "📊 *Stocks / ETFs* `📋 DEMO`\n"
        "├ SPY `$521.44` `+0.31%` ✅\n"
        "├ QQQ `$442.10` `+0.52%` ✅\n"
        "├ IWM `$201.30` `−0.12%` ❌\n"
        "└ DIA `$389.20` `+0.08%` ✅\n\n"
        "🏅 *Commodities* `📋 DEMO`\n"
        "├ GLD `$231.75` `+0.18%` ✅\n"
        "└ USO `$74.20`  `+0.54%` ✅\n\n"
        f"🕐 `{ts_now()}`"
    )
    keyboard = kb(
        [("🔄 Refresh",   "td_market"), ("✏️ Trade Now", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN 6: Trade History ─────────────────────────────────────────────────
def screen_history(uid):
    trades = sorted(
        get_user_trades(uid),
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )[:5]

    if not trades:
        body = "_No trades yet._\n\nStart with Manual Trade."
    else:
        rows = []
        for i, t in enumerate(trades, 1):
            side = t.get("side", "?")
            sym = t.get("symbol", "?")
            pnl = t.get("pnl", 0)
            mode = t.get("mode", "PAPER")
            icon = "✅" if pnl >= 0 else "❌"
            sign = "+" if pnl >= 0 else ""
            tag = "🔴" if mode == "LIVE" else "🧪"
            rows.append(f"{i}️⃣  {tag} {sym} · {side} {icon}  `{sign}{pnl:.2f}`")
        body = "\n\n".join(rows)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Trade History*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}\n\n"
        "_🔴 Live · 🧪 Paper_"
    )
    keyboard = kb(
        [("📊 Statistics", "td_stats"), ("🔄 Refresh", "td_history")],
        [("⬅️ Dashboard",  "td_home")],
    )
    return text, keyboard


# ─── SCREEN 7: Statistics ────────────────────────────────────────────────────
def screen_stats(uid):
    trades = get_user_trades(uid)
    total = len(trades)
    wins = sum(1 for t in trades if t.get("pnl", 0) >= 0)
    losses = total - wins
    net_pnl = sum(t.get("pnl", 0) for t in trades)
    wr = f"{wins / total * 100:.1f}%" if total else "—"
    sign = "+" if net_pnl >= 0 else ""
    live_count = sum(1 for t in trades if t.get("mode") == "LIVE")
    paper_count = total - live_count

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Performance Stats*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏆 *All Time*\n"
        f"├ Total Trades: `{total}`\n"
        f"├ Live trades:  `{live_count}`\n"
        f"├ Paper trades: `{paper_count}`\n"
        f"├ Win Rate:     `{wr}`\n"
        f"├ Winners:      `{wins}`\n"
        f"├ Losers:       `{losses}`\n"
        f"└ Net P&L:      `{sign}{net_pnl:.2f}`"
    )
    keyboard = kb(
        [("📋 Trade History", "td_history"), ("🤖 Auto Trading", "td_auto")],
        [("⬅️ Dashboard",     "td_home")],
    )
    return text, keyboard


# ─── SCREEN 8: Bot Settings ──────────────────────────────────────────────────
def screen_settings(uid):
    accts = _load("accounts").get(str(uid), {})

    def conn(name):
        a = accts.get(name, {})
        s = a.get("status", "not_set")
        if s == "connected": return "🟢 Connected"
        if s == "error":     return "🔴 Error"
        if a.get("api_key"): return "🟡 Unverified"
        return "⬜ Not set"

    live = BINANCE_LOADED and is_live_mode(uid)
    mode_str = "🔴 LIVE (real orders)" if live else "🧪 PAPER (safe)"
    toggle_label = "🧪 Switch to PAPER" if live else "🔴 Enable LIVE MODE"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *Bot Settings*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔗 *Exchanges*\n"
        f"├ Binance: `{conn('binance')}`\n"
        f"├ Alpaca:  `{conn('alpaca')}`\n"
        f"├ eToro:   `{conn('etoro')}`\n"
        f"└ Exness:  `{conn('exness')}`\n\n"
        "🤖 *Trading Mode*\n"
        f"└ `{mode_str}`\n\n"
        "_Verify your Binance key before_\n"
        "_enabling Live Mode._"
    )
    keyboard = kb(
        [("✅ Verify Binance", "settings_verify")],
        [(toggle_label, "settings_toggle_mode")],
        [("🔗 Manage APIs", "main_trading_menu"), ("🔔 Alerts", "settings_notif")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


def screen_verify(uid):
    if not BINANCE_LOADED:
        return ("❌ python-binance not loaded.",
                kb([("⬅️ Back", "td_settings")]))
    creds = get_user_binance_creds(uid)
    if not creds:
        return ("⚠️ No Binance API key found.\n\n"
                "Add via *Trading Menu → Binance*.",
                kb([("⬅️ Back", "td_settings")]))
    try:
        client = BinanceClient(*creds)
        ok, msg = client.verify_credentials()
    except Exception as e:
        ok, msg = False, f"❌ Error: {e}"

    if ok:
        bal = client.get_balance("USDT")
        text = (
            "✅ *Binance Connection Verified*\n\n"
            f"{msg}\n\n"
            f"💰 USDT Balance: `{fmt_usd(bal)}`\n\n"
            "Safe to enable Live Mode."
        )
    else:
        text = "❌ *Verification Failed*\n\n" + msg
    return text, kb([("⬅️ Back", "td_settings")])


def screen_toggle_mode(uid):
    currently_live = BINANCE_LOADED and is_live_mode(uid)
    if currently_live:
        set_live_mode(uid, False)
        text = (
            "🧪 *Switched to PAPER MODE*\n\n"
            "No real orders will be placed."
        )
        return text, kb([("⬅️ Settings", "td_settings")])

    if not BINANCE_LOADED:
        return "❌ Binance module not loaded.", kb([("⬅️ Back", "td_settings")])
    if not get_user_binance_creds(uid):
        return ("⚠️ Connect Binance API first.",
                kb([("🔗 Connect Binance", "main_trading_menu"),
                    ("⬅️ Back", "td_settings")]))

    text = (
        "⚠️ *Enable LIVE MODE?*\n\n"
        "Every BUY/SELL will place a\n"
        "*REAL ORDER* on Binance.\n\n"
        "🛡 Safety guards stay active:\n"
        f"├ Max per trade: `${MAX_USD_PER_TRADE}`\n"
        "├ Whitelist: `BTC, ETH, BNB, SOL`\n"
        "└ Withdraw key permission: OFF\n\n"
        "Are you sure?"
    )
    keyboard = kb(
        [("🔴 YES — Enable LIVE", "settings_confirm_live")],
        [("❌ Cancel", "td_settings")],
    )
    return text, keyboard


def screen_confirm_live(uid):
    set_live_mode(uid, True)
    text = (
        "🔴 *LIVE MODE ENABLED*\n\n"
        "Real orders are now active.\n"
        "Trade carefully.\n\n"
        "Switch back to Paper anytime."
    )
    return text, kb([("📊 Dashboard", "td_home"), ("⚙️ Settings", "td_settings")])


# ─── Confirm Order ───────────────────────────────────────────────────────────
def screen_confirm(side, symbol, uid):
    is_crypto = symbol.upper() in LIVE_SYMBOLS
    has_creds = BINANCE_LOADED and get_user_binance_creds(uid) is not None
    will_be_live = is_crypto and has_creds and is_live_mode(uid)

    badge = "🔴 *LIVE — REAL MONEY*" if will_be_live else "🧪 *PAPER — no real funds*"
    emoji = "🟢" if side == "buy" else "🔴"
    verb = side.upper()

    size_line = ""
    if will_be_live and side == "buy":
        client = get_client_for_user(uid)
        if client:
            usdt = client.get_balance("USDT")
            size = calc_trade_size_usd(usdt)
            size_line = f"Amount: `{fmt_usd(size)}` _(1% of {fmt_usd(usdt)})_\n"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *Confirm {verb}*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"Asset:  `{symbol}`\n"
        f"Side:   `{verb}`\n"
        f"Type:   `Market`\n"
        f"{size_line}"
        "\nConfirm?"
    )
    keyboard = kb(
        [(f"✅ Confirm {verb}", f"confirm_{side}_{symbol}"),
         ("❌ Cancel", "td_manual")],
    )
    return text, keyboard


# ─── Order Placed ────────────────────────────────────────────────────────────
def screen_filled(side, symbol, uid):
    is_crypto = symbol.upper() in LIVE_SYMBOLS
    has_creds = BINANCE_LOADED and get_user_binance_creds(uid) is not None
    go_live = is_crypto and has_creds and is_live_mode(uid)

    if go_live:
        client = get_client_for_user(uid)
        if not client:
            return ("❌ Binance client init failed.",
                    kb([("⬅️ Back", "td_manual")]))

        if side == "buy":
            usdt = client.get_balance("USDT")
            size = calc_trade_size_usd(usdt)
            if usdt < size:
                return (f"❌ Need `{fmt_usd(size)}` USDT, have `{fmt_usd(usdt)}`.",
                        kb([("⬅️ Back", "td_manual")]))
            result = client.place_market_buy(symbol, size)
        else:
            asset = to_binance_symbol(symbol).replace("USDT", "")
            qty = client.get_balance(asset)
            if qty <= 0:
                return (f"❌ No {asset} balance to sell.",
                        kb([("⬅️ Back", "td_manual")]))
            result = client.place_market_sell(symbol, qty)

        if not result.get("success"):
            text = (
                "❌ *Order Failed*\n\n"
                f"Symbol: `{symbol}`\n"
                f"Side:   `{side.upper()}`\n"
                f"Error:  `{result.get('error')}`\n\n"
                "_No funds moved._"
            )
            return text, kb(
                [("📋 History", "td_history"), ("⬅️ Back", "td_manual")],
            )

        trades = _load("trades")
        tid = f"TRADE_{uid}_{int(datetime.now(timezone.utc).timestamp())}"
        trades[tid] = {
            "trade_id":    tid,
            "user_id":     int(uid),
            "symbol":      result["symbol"],
            "side":        side.upper(),
            "type":        "MANUAL",
            "mode":        "LIVE",
            "order_type":  "MARKET",
            "status":      "OPEN" if side == "buy" else "CLOSED",
            "binance_order_id": result["order_id"],
            "entry_price": result["fill_price"],
            "qty":         result["qty"],
            "pnl":         0,
            "created_at":  datetime.now(timezone.utc).isoformat(),
        }
        _save("trades", trades)

        emoji = "🟢" if side == "buy" else "🔴"
        text = (
            "✅ *LIVE Order Filled!*\n\n"
            f"{emoji} {side.upper()} `{result['symbol']}`\n"
            f"Fill price: `{fmt_usd(result['fill_price'])}`\n"
            f"Quantity:   `{result['qty']:.6f}`\n"
            f"Order ID:   `{result['order_id']}`\n"
            f"Time:       `{ts_now()}`\n\n"
            "_Verify on Binance to confirm._"
        )
        return text, kb(
            [("📋 History", "td_history"), ("🏠 Dashboard", "td_home")],
        )

    # Paper path
    trades = _load("trades")
    tid = f"TRADE_{uid}_{int(datetime.now(timezone.utc).timestamp())}"
    trades[tid] = {
        "trade_id":    tid,
        "user_id":     int(uid),
        "symbol":      symbol,
        "side":        side.upper(),
        "type":        "MANUAL",
        "mode":        "PAPER",
        "order_type":  "MARKET",
        "status":      "OPEN",
        "entry_price": 0,
        "qty":         0,
        "pnl":         0,
        "created_at":  datetime.now(timezone.utc).isoformat(),
    }
    _save("trades", trades)

    emoji = "🟢" if side == "buy" else "🔴"
    text = (
        "✅ *Paper Order Placed*\n\n"
        f"{emoji} {side.upper()} `{symbol}`\n"
        f"Status: `Filled (Paper)`\n"
        f"Time:   `{ts_now()}`\n\n"
        "_No real funds — paper trade._"
    )
    return text, kb(
        [("📋 History", "td_history"), ("🏠 Dashboard", "td_home")],
    )


# ─── /trading COMMAND ────────────────────────────────────────────────────────
async def cmd_trading_dashboard(update, ctx):
    uid = str(update.effective_user.id)
    text, keyboard = screen_trading_home(uid)
    await update.message.reply_text(
        text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )


# ─── CALLBACK ROUTER ─────────────────────────────────────────────────────────
async def handle_trading_callbacks(update, ctx):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)

    text, keyboard = None, None

    if   data == "td_home":     text, keyboard = screen_trading_home(uid)
    elif data == "td_auto":     text, keyboard = screen_auto(uid)
    elif data == "td_manual":   text, keyboard = screen_manual()
    elif data == "td_market":   text, keyboard = screen_market(uid)
    elif data == "td_history":  text, keyboard = screen_history(uid)
    elif data == "td_stats":    text, keyboard = screen_stats(uid)
    elif data == "td_settings": text, keyboard = screen_settings(uid)

    elif data == "settings_verify":        text, keyboard = screen_verify(uid)
    elif data == "settings_toggle_mode":   text, keyboard = screen_toggle_mode(uid)
    elif data == "settings_confirm_live":  text, keyboard = screen_confirm_live(uid)
    elif data == "settings_notif":
        text = "🔔 *Notifications*\n\n✅ All Telegram alerts active."
        keyboard = kb([("⬅️ Settings", "td_settings")])

    elif data.startswith("mt_"):
        text, keyboard = screen_trade_detail(data[3:], uid)

    elif data.startswith("exec_buy_"):
        text, keyboard = screen_confirm("buy", data[9:], uid)
    elif data.startswith("exec_sell_"):
        text, keyboard = screen_confirm("sell", data[10:], uid)

    elif data.startswith("confirm_buy_"):
        text, keyboard = screen_filled("buy", data[12:], uid)
    elif data.startswith("confirm_sell_"):
        text, keyboard = screen_filled("sell", data[13:], uid)

    elif data == "bot_start":
        text = ("🤖 *Bot Starting...*\n\n"
                "⚠️ Auto engine is Phase 4.\n"
                "Use Manual Trade for now.")
        keyboard = kb([("⬅️ Back", "td_auto")])
    elif data == "bot_config":
        text = (
            "🔧 *Bot Configuration*\n\n"
            "├ Risk/Trade:  `1%`\n"
            f"├ Max/Trade:   `${MAX_USD_PER_TRADE}`\n"
            "├ Stop Loss:   `2%`\n"
            "├ Take Profit: `3%`\n"
            "└ Symbols:     `BTC, ETH, BNB, SOL`"
        )
        keyboard = kb([("⬅️ Back", "td_auto")])

    if text is None:
        return

    try:
        await query.edit_message_text(
            text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.warning(f"edit_message_text failed: {e}")
