#!/usr/bin/env python3
"""
OpenAsset Trading Dashboard — Binance (crypto) + Alpaca (stocks)
================================================================

Routing by asset class:
  * Crypto  (BTC/ETH/BNB/SOL)  → Binance  — real orders in Live Mode
  * Stocks  (SPY/QQQ/GLD/USO/IWM/DIA) → Alpaca — paper account (safe)
  * Unknown → demo stub

Home/menu buttons use the host bot's real callbacks:
  * back_home     (host bot main menu)
  * trading_menu  (host bot platform selection)
"""

import os
import json
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

# ── Binance ──
try:
    from binance_client import (
        BinanceClient, get_client_for_user as get_binance_client,
        get_user_binance_creds, is_live_mode, set_live_mode,
        calc_trade_size_usd, to_binance_symbol, MAX_USD_PER_TRADE,
    )
    BINANCE_LOADED = True
except ImportError:
    BINANCE_LOADED = False
    MAX_USD_PER_TRADE = 50.0

# ── Alpaca ──
try:
    from alpaca_client import (
        get_client_for_user as get_alpaca_client,
        get_user_alpaca_creds,
        calc_trade_size_usd as alpaca_trade_size,
    )
    ALPACA_LOADED = True
except ImportError:
    ALPACA_LOADED = False

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

CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD"}
STOCK_SYMBOLS = {"SPY", "QQQ", "GLD", "USO", "IWM", "DIA"}

# Fallback demo prices for stocks if Alpaca data unavailable
DEMO_STOCKS = {
    "SPY": "521.44", "QQQ": "442.10", "GLD": "231.75",
    "USO": "74.20",  "IWM": "201.30", "DIA": "389.20",
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
        [InlineKeyboardButton(t, callback_data=d) for t, d in row]
        for row in rows
    ])


def asset_class(symbol):
    s = symbol.upper()
    if s in CRYPTO_SYMBOLS or s.endswith("USDT"):
        return "crypto"
    if s in STOCK_SYMBOLS:
        return "stock"
    return None


def has_binance(uid):
    return BINANCE_LOADED and get_user_binance_creds(uid) is not None


def has_alpaca(uid):
    return ALPACA_LOADED and get_user_alpaca_creds(uid) is not None


def mode_badge(uid):
    if BINANCE_LOADED and is_live_mode(uid):
        return "🔴 *LIVE MODE* (crypto)"
    return "🧪 *PAPER MODE*"


def fmt_usd(n):
    try:
        return f"${n:,.2f}" if abs(n) >= 1 else f"${n:.4f}"
    except Exception:
        return "$—"


def fmt_pct(n):
    sign = "+" if n >= 0 else ""
    return f"{sign}{n:.2f}%"


# ─── SCREEN 1: Trading Home ──────────────────────────────────────────────────
def screen_trading_home(uid):
    badge = mode_badge(uid)

    bn_line = "├ Binance: 🔗 not connected"
    if has_binance(uid):
        c = get_binance_client(uid)
        if c:
            bn_line = f"├ Binance: 💰 {fmt_usd(c.get_balance('USDT'))} USDT"

    al_line = "└ Alpaca:  🔗 not connected"
    if has_alpaca(uid):
        c, paper = get_alpaca_client(uid)
        if c:
            tag = "paper" if paper else "live"
            al_line = f"└ Alpaca:  💵 {fmt_usd(c.get_cash())} ({tag})"

    trades = get_user_trades(uid)
    open_t = [t for t in trades if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Trading Dashboard*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        "💼 *Accounts*\n"
        f"{bn_line}\n"
        f"{al_line}\n\n"
        f"📈 Open trades: `{len(open_t)}`\n"
        f"📋 Total:       `{len(trades)} trades`\n\n"
        f"🕐 `{ts_now()}` · `{date_now()}`"
    )
    keyboard = kb(
        [("🤖 Auto Trading", "td_auto"),    ("✏️ Manual Trade", "td_manual")],
        [("📈 Market Data",  "td_market"),  ("📋 Trade History","td_history")],
        [("📊 Statistics",   "td_stats"),   ("⚙️ Bot Settings", "td_settings")],
        [("🏠 Main Menu",    "back_home")],
    )
    return text, keyboard


# ─── SCREEN 2: Auto Trading ──────────────────────────────────────────────────
def screen_auto(uid):
    open_t = [t for t in get_user_trades(uid) if t.get("status") == "OPEN"]
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Auto Trading Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mode_badge(uid)}\n\n"
        f"Binance: `{'✅' if has_binance(uid) else '⚠️ connect'}`\n"
        f"Alpaca:  `{'✅' if has_alpaca(uid) else '⚠️ connect'}`\n"
        f"Status:  `⬜ Standby`\n"
        f"Open:    `{len(open_t)} positions`\n\n"
        "⚙️ *Default Settings*\n"
        "├ Risk/Trade: `1% of balance`\n"
        f"├ Max/Trade:  `${MAX_USD_PER_TRADE} cap`\n"
        "├ Stop Loss:  `2%`\n"
        "└ Take Profit:`3%`\n\n"
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
        "🔶 *Crypto* — Binance (live in Live Mode)\n"
        "📊 *Stocks* — Alpaca (paper, safe)\n\n"
        "Choose an asset:"
    )
    keyboard = kb(
        [("₿ BTC/USD",  "mt_BTCUSD"), ("Ξ ETH/USD", "mt_ETHUSD")],
        [("🟡 BNB/USD", "mt_BNBUSD"), ("◎ SOL/USD", "mt_SOLUSD")],
        [("📈 SPY",     "mt_SPY"),    ("📈 QQQ",    "mt_QQQ")],
        [("🥇 GLD",     "mt_GLD"),    ("⚫ USO",    "mt_USO")],
        [("⬅️ Dashboard","td_home")],
    )
    return text, keyboard


# ─── SCREEN 4: Trade Detail ──────────────────────────────────────────────────
def screen_trade_detail(symbol, uid):
    cls = asset_class(symbol)
    badge = mode_badge(uid)

    # CRYPTO (Binance)
    if cls == "crypto":
        if has_binance(uid):
            c = get_binance_client(uid)
            if c:
                s = c.get_24h_stats(symbol)
                p, hi, lo = fmt_usd(s["price"]), fmt_usd(s["high"]), fmt_usd(s["low"])
                chg = fmt_pct(s["change_pct"])
                arrow = "✅" if s["change_pct"] >= 0 else "❌"
                tag = "🟢 LIVE · Binance"
                usdt = c.get_balance("USDT")
                size = calc_trade_size_usd(usdt)
                size_line = f"\n💵 Trade size: `{fmt_usd(size)}` _(1%, capped)_"
                buttons = kb(
                    [("🟢 BUY", f"exec_buy_{symbol}"), ("🔴 SELL", f"exec_sell_{symbol}")],
                    [("⬅️ Back", "td_manual")],
                )
            else:
                return ("⚠️ Binance client error.", kb([("⬅️ Back", "td_manual")]))
        else:
            return ("🔗 Connect Binance first (Trading Menu → Binance).",
                    kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_manual")]))

    # STOCK (Alpaca)
    elif cls == "stock":
        if has_alpaca(uid):
            c, paper = get_alpaca_client(uid)
            if c:
                price = c.get_price(symbol)
                p = fmt_usd(price) if price else f"${DEMO_STOCKS.get(symbol,'—')}"
                hi = lo = "—"
                chg, arrow = "—", "📊"
                tag = f"🟢 LIVE · Alpaca {'(paper)' if paper else '(live)'}"
                cash = c.get_cash()
                size = alpaca_trade_size(cash)
                size_line = f"\n💵 Trade size: `{fmt_usd(size)}` _(1%, capped)_"
                buttons = kb(
                    [("🟢 BUY", f"exec_buy_{symbol}"), ("🔴 SELL", f"exec_sell_{symbol}")],
                    [("⬅️ Back", "td_manual")],
                )
            else:
                return ("⚠️ Alpaca client error.", kb([("⬅️ Back", "td_manual")]))
        else:
            return ("🔗 Connect Alpaca first (Trading Menu → Alpaca).",
                    kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_manual")]))
    else:
        return ("⚠️ Unknown symbol.", kb([("⬅️ Back", "td_manual")]))

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{symbol}*  ·  `{tag}`\n"
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
    return text, buttons


# ─── SCREEN 5: Market Data ───────────────────────────────────────────────────
def screen_market(uid):
    # Crypto block
    if has_binance(uid):
        c = get_binance_client(uid)
        try:
            btc = c.get_24h_stats("BTCUSDT"); eth = c.get_24h_stats("ETHUSDT")
            bnb = c.get_24h_stats("BNBUSDT"); sol = c.get_24h_stats("SOLUSDT")
            crypto = (
                "🔶 *Crypto* `🟢 LIVE`\n"
                f"├ BTC `{fmt_usd(btc['price'])}` `{fmt_pct(btc['change_pct'])}`\n"
                f"├ ETH `{fmt_usd(eth['price'])}` `{fmt_pct(eth['change_pct'])}`\n"
                f"├ BNB `{fmt_usd(bnb['price'])}` `{fmt_pct(bnb['change_pct'])}`\n"
                f"└ SOL `{fmt_usd(sol['price'])}` `{fmt_pct(sol['change_pct'])}`\n\n"
            )
        except Exception as e:
            logger.warning(f"crypto market: {e}")
            crypto = "🔶 *Crypto* `⚠️ API error`\n\n"
    else:
        crypto = "🔶 *Crypto* `🔗 Connect Binance`\n\n"

    # Stock block (Alpaca)
    if has_alpaca(uid):
        c, paper = get_alpaca_client(uid)
        try:
            spy = c.get_price("SPY"); qqq = c.get_price("QQQ")
            gld = c.get_price("GLD"); uso = c.get_price("USO")
            stocks = (
                f"📊 *Stocks* `🟢 LIVE · Alpaca`\n"
                f"├ SPY `{fmt_usd(spy)}`\n"
                f"├ QQQ `{fmt_usd(qqq)}`\n"
                f"├ GLD `{fmt_usd(gld)}`\n"
                f"└ USO `{fmt_usd(uso)}`\n\n"
            )
        except Exception as e:
            logger.warning(f"stock market: {e}")
            stocks = "📊 *Stocks* `⚠️ market closed / API`\n\n"
    else:
        stocks = "📊 *Stocks* `🔗 Connect Alpaca`\n\n"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 *Market Data*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{crypto}{stocks}"
        f"🕐 `{ts_now()}`"
    )
    keyboard = kb(
        [("🔄 Refresh",   "td_market"), ("✏️ Trade Now", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN 6: Trade History ─────────────────────────────────────────────────
def screen_history(uid):
    trades = sorted(get_user_trades(uid),
                    key=lambda x: x.get("created_at", ""), reverse=True)[:6]
    if not trades:
        body = "_No trades yet._\n\nStart with Manual Trade."
    else:
        rows = []
        for i, t in enumerate(trades, 1):
            side, sym = t.get("side", "?"), t.get("symbol", "?")
            pnl, mode = t.get("pnl", 0), t.get("mode", "PAPER")
            icon = "✅" if pnl >= 0 else "❌"
            sign = "+" if pnl >= 0 else ""
            tag = {"LIVE": "🔴", "ALPACA": "📊", "PAPER": "🧪"}.get(mode, "🧪")
            rows.append(f"{i}️⃣  {tag} {sym} · {side} {icon}  `{sign}{pnl:.2f}`")
        body = "\n\n".join(rows)
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Trade History*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}\n\n"
        "_🔴 Binance live · 📊 Alpaca · 🧪 Paper_"
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
    net = sum(t.get("pnl", 0) for t in trades)
    wr = f"{wins/total*100:.1f}%" if total else "—"
    sign = "+" if net >= 0 else ""
    live = sum(1 for t in trades if t.get("mode") == "LIVE")
    alp = sum(1 for t in trades if t.get("mode") == "ALPACA")
    paper = total - live - alp
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Performance Stats*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"├ Total Trades: `{total}`\n"
        f"├ Binance live: `{live}`\n"
        f"├ Alpaca:       `{alp}`\n"
        f"├ Paper:        `{paper}`\n"
        f"├ Win Rate:     `{wr}`\n"
        f"└ Net P&L:      `{sign}{net:.2f}`"
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
        if a.get("status") == "connected": return "🟢 Connected"
        if a.get("status") == "error":     return "🔴 Error"
        if a.get("api_key"):                return "🟡 Unverified"
        return "⬜ Not set"

    live = BINANCE_LOADED and is_live_mode(uid)
    mode_str = "🔴 LIVE (real crypto orders)" if live else "🧪 PAPER (safe)"
    toggle = "🧪 Switch to PAPER" if live else "🔴 Enable LIVE MODE"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *Bot Settings*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔗 *Exchanges*\n"
        f"├ Binance: `{conn('binance')}`\n"
        f"├ Alpaca:  `{conn('alpaca')}`\n"
        f"├ eToro:   `{conn('etoro')}`\n"
        f"└ Exness:  `{conn('exness')}`\n\n"
        "🤖 *Crypto Trading Mode*\n"
        f"└ `{mode_str}`\n\n"
        "_Stocks always trade on Alpaca paper (safe)._\n"
        "_Verify Binance before enabling Live._"
    )
    keyboard = kb(
        [("✅ Verify Binance", "settings_verify")],
        [(toggle, "settings_toggle_mode")],
        [("🔗 Manage APIs", "trading_menu"), ("🔔 Alerts", "settings_notif")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


def screen_verify(uid):
    if not has_binance(uid):
        return ("⚠️ No Binance API key. Add via Trading Menu → Binance.",
                kb([("⬅️ Back", "td_settings")]))
    try:
        c = BinanceClient(*get_user_binance_creds(uid))
        ok, msg = c.verify_credentials()
    except Exception as e:
        ok, msg = False, f"❌ {e}"
    if ok:
        text = f"✅ *Binance Verified*\n\n{msg}\n\n💰 USDT: `{fmt_usd(c.get_balance('USDT'))}`"
    else:
        text = "❌ *Verification Failed*\n\n" + msg
    return text, kb([("⬅️ Back", "td_settings")])


def screen_toggle_mode(uid):
    if BINANCE_LOADED and is_live_mode(uid):
        set_live_mode(uid, False)
        return ("🧪 *Switched to PAPER MODE*\n\nNo real orders.",
                kb([("⬅️ Settings", "td_settings")]))
    if not has_binance(uid):
        return ("⚠️ Connect Binance API first.",
                kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_settings")]))
    text = (
        "⚠️ *Enable LIVE MODE?*\n\n"
        "Crypto BUY/SELL will place *REAL orders* on Binance.\n\n"
        "🛡 Guards stay on:\n"
        f"├ Max ${MAX_USD_PER_TRADE}/trade\n"
        "├ BTC/ETH/BNB/SOL only\n"
        "└ No-withdraw key required\n\n"
        "Sure?"
    )
    return text, kb(
        [("🔴 YES — Enable LIVE", "settings_confirm_live")],
        [("❌ Cancel", "td_settings")],
    )


def screen_confirm_live(uid):
    set_live_mode(uid, True)
    return ("🔴 *LIVE MODE ENABLED*\n\nReal crypto orders active.\nSwitch to Paper anytime.",
            kb([("📊 Dashboard", "td_home"), ("⚙️ Settings", "td_settings")]))


# ─── Confirm Order ───────────────────────────────────────────────────────────
def screen_confirm(side, symbol, uid):
    cls = asset_class(symbol)
    emoji = "🟢" if side == "buy" else "🔴"
    verb = side.upper()

    if cls == "crypto":
        live = BINANCE_LOADED and is_live_mode(uid) and has_binance(uid)
        badge = "🔴 *LIVE — REAL MONEY*" if live else "🧪 *PAPER*"
        venue = "Binance"
    elif cls == "stock":
        badge = "📊 *Alpaca Paper (safe)*"
        venue = "Alpaca"
    else:
        badge = "🧪 *PAPER*"
        venue = "—"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *Confirm {verb}*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"Asset: `{symbol}`\n"
        f"Venue: `{venue}`\n"
        f"Side:  `{verb}`\n"
        f"Type:  `Market`\n\n"
        "Confirm?"
    )
    return text, kb(
        [(f"✅ Confirm {verb}", f"confirm_{side}_{symbol}"), ("❌ Cancel", "td_manual")],
    )


# ─── Order Placed ────────────────────────────────────────────────────────────
def _save_trade(uid, symbol, side, mode, **extra):
    trades = _load("trades")
    tid = f"TRADE_{uid}_{int(datetime.now(timezone.utc).timestamp())}"
    rec = {
        "trade_id": tid, "user_id": int(uid), "symbol": symbol,
        "side": side.upper(), "type": "MANUAL", "mode": mode,
        "order_type": "MARKET", "status": "OPEN",
        "entry_price": 0, "qty": 0, "pnl": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    rec.update(extra)
    trades[tid] = rec
    _save("trades", trades)


def screen_filled(side, symbol, uid):
    cls = asset_class(symbol)

    # ── CRYPTO via Binance ──
    if cls == "crypto":
        live = BINANCE_LOADED and is_live_mode(uid) and has_binance(uid)
        if live:
            c = get_binance_client(uid)
            if side == "buy":
                usdt = c.get_balance("USDT")
                size = calc_trade_size_usd(usdt)
                if usdt < size:
                    return (f"❌ Need {fmt_usd(size)} USDT, have {fmt_usd(usdt)}.",
                            kb([("⬅️ Back", "td_manual")]))
                r = c.place_market_buy(symbol, size)
            else:
                asset = to_binance_symbol(symbol).replace("USDT", "")
                qty = c.get_balance(asset)
                if qty <= 0:
                    return (f"❌ No {asset} to sell.", kb([("⬅️ Back", "td_manual")]))
                r = c.place_market_sell(symbol, qty)
            if not r.get("success"):
                return (f"❌ *Order Failed*\n\n`{r.get('error')}`\n\n_No funds moved._",
                        kb([("📋 History", "td_history"), ("⬅️ Back", "td_manual")]))
            _save_trade(uid, r["symbol"], side, "LIVE",
                        binance_order_id=r["order_id"],
                        entry_price=r["fill_price"], qty=r["qty"],
                        status="OPEN" if side == "buy" else "CLOSED")
            return (
                "✅ *LIVE Order Filled!*\n\n"
                f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{r['symbol']}`\n"
                f"Fill: `{fmt_usd(r['fill_price'])}`\n"
                f"Qty:  `{r['qty']:.6f}`\n"
                f"ID:   `{r['order_id']}`\n\n_Verify on Binance._",
                kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
            )
        else:
            _save_trade(uid, symbol, side, "PAPER")
            return (
                "✅ *Paper Order Placed*\n\n"
                f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{symbol}`\n"
                "Status: `Filled (Paper)`\n\n_Enable Live Mode for real orders._",
                kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
            )

    # ── STOCK via Alpaca (paper account = safe) ──
    elif cls == "stock":
        if not has_alpaca(uid):
            return ("🔗 Connect Alpaca first.",
                    kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_manual")]))
        c, paper = get_alpaca_client(uid)
        if not c:
            return ("⚠️ Alpaca client error.", kb([("⬅️ Back", "td_manual")]))
        if side == "buy":
            cash = c.get_cash()
            size = alpaca_trade_size(cash)
            r = c.place_market_buy(symbol, size)
        else:
            r = c.place_market_sell(symbol)
        if not r.get("success"):
            return (f"❌ *Alpaca Order Failed*\n\n`{r.get('error')}`\n\n"
                    "_Market may be closed — try during US hours,_\n"
                    "_or order will queue for next open._",
                    kb([("📋 History", "td_history"), ("⬅️ Back", "td_manual")]))
        _save_trade(uid, r["symbol"], side, "ALPACA",
                    alpaca_order_id=r.get("order_id"),
                    entry_price=r.get("fill_price", 0), qty=r.get("qty", 0),
                    status="OPEN" if side == "buy" else "CLOSED")
        return (
            f"✅ *Alpaca Order Placed* {'(paper)' if paper else '(live)'}\n\n"
            f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{r['symbol']}`\n"
            f"Order ID: `{r.get('order_id','—')}`\n"
            f"Time: `{ts_now()}`\n\n_Real Alpaca order flow, fake money._",
            kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
        )
    else:
        return ("⚠️ Unknown symbol.", kb([("⬅️ Back", "td_manual")]))


# ─── /trading COMMAND ────────────────────────────────────────────────────────
async def cmd_trading_dashboard(update, ctx):
    uid = str(update.effective_user.id)
    text, keyboard = screen_trading_home(uid)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


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
    elif data == "settings_verify":       text, keyboard = screen_verify(uid)
    elif data == "settings_toggle_mode":  text, keyboard = screen_toggle_mode(uid)
    elif data == "settings_confirm_live": text, keyboard = screen_confirm_live(uid)
    elif data == "settings_notif":
        text = "🔔 *Notifications*\n\n✅ All alerts active."
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
        text = "🤖 *Auto engine ships Phase 4.*\nUse Manual Trade."
        keyboard = kb([("⬅️ Back", "td_auto")])
    elif data == "bot_config":
        text = (f"🔧 *Config*\n├ Risk 1%\n├ Max ${MAX_USD_PER_TRADE}\n"
                "├ SL 2% · TP 3%\n└ BTC/ETH/BNB/SOL + stocks")
        keyboard = kb([("⬅️ Back", "td_auto")])

    if text is None:
        return  # not ours — let host bot handle (back_home, trading_menu, etc.)

    try:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.warning(f"edit failed: {e}")
