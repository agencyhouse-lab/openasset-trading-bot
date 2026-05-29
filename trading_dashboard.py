#!/usr/bin/env python3
"""
OpenAsset Trading Dashboard
============================
Three trading venues, one dashboard:

  * 🔶 Binance     — live crypto (real money in LIVE mode)
  * 📊 Alpaca      — live US stocks/ETFs (real money)
  * 🏛 Strategy Lab — practice trading, $10k balance, 40+ assets,
                     real prices, instant fills, real SL/TP enforcement

Universal back_home intercept fixes the Help/FAQ/Guide back buttons.
Admin gets notified on every LIVE money trade.
"""

import os
import json
import logging
import threading
from datetime import datetime, timezone

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

# ─── Binance ────────────────────────────────────────────────────────────────
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

# ─── Alpaca ─────────────────────────────────────────────────────────────────
try:
    from alpaca_client import (
        get_client_for_user as get_alpaca_client,
        get_user_alpaca_creds,
        calc_trade_size_usd as alpaca_trade_size,
    )
    ALPACA_LOADED = True
except ImportError:
    ALPACA_LOADED = False

# ─── Strategy Lab (OpenAsset Internal) ──────────────────────────────────────
try:
    from openasset_engine import (
        place_market_buy as oa_buy, close_position as oa_close,
        set_sl_tp as oa_set_sl_tp, get_cash as oa_cash,
        get_positions as oa_positions, get_portfolio_value as oa_value,
        get_unrealized_pnl as oa_unrealized, get_trades as oa_trades_fn,
        get_position as oa_get_pos, reset_account as oa_reset_acct,
        STARTING_CASH as OA_START, MAX_USD_PER_TRADE as OA_MAX,
    )
    from openasset_feeds import (
        get_price as oa_price, get_symbol_info as oa_sym_info,
        list_symbols as oa_list_symbols, list_classes as oa_list_classes,
        display_name as oa_display, asset_class_of as oa_class_of,
        CLASS_EMOJI as OA_CLASS_EMOJI, CLASS_LABEL as OA_CLASS_LABEL,
        get_market_status as oa_market_status,
        format_time_until as oa_fmt_time,
    )
    STRATLAB_LOADED = True
except ImportError as e:
    STRATLAB_LOADED = False
    logging.getLogger(__name__).warning(f"Strategy Lab not loaded: {e}")

logger = logging.getLogger(__name__)

ADMIN_ID = 5587885687
ADMIN_BOT_TOKEN = "8759490386:AAGy3QzviccZzRkXHYmD7EHYtICvToQO3yU"
DB_PATH = "/root/openasset_club/telegram_bot/database"

# Safe-by-default trading rules (displayed everywhere)
STOP_LOSS_PCT = 0.5
TAKE_PROFIT_PCT = 3.0
RISK_PCT = 1.0

# All callbacks owned by this module. back_home intercepted to fix host bugs.
TRADING_CALLBACK_PATTERN = (
    r"^(td_home|td_mainmenu|td_auto|td_manual|td_market|td_history|"
    r"td_stats|td_settings|td_psychology|td_pause_|td_resume_|td_stopall|"
    r"mt_|exec_buy_|exec_sell_|confirm_buy_|confirm_sell_|"
    r"settings_notif|settings_verify|settings_toggle_mode|settings_confirm_live|"
    r"oa_|back_home)"
)

CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD"}
STOCK_SYMBOLS = {"SPY", "QQQ", "GLD", "USO", "IWM", "DIA"}


# ─── DB ──────────────────────────────────────────────────────────────────────
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


def get_user_trades(uid):
    return [t for t in _load("trades").values()
            if str(t.get("user_id")) == str(uid)]


def is_paused(uid, platform):
    return _load("accounts").get(str(uid), {}).get(platform, {}).get("paused", False) is True


def set_paused(uid, platform, paused):
    a = _load("accounts")
    a.setdefault(str(uid), {}).setdefault(platform, {})["paused"] = bool(paused)
    _save("accounts", a)


def set_all_paused(uid, paused):
    a = _load("accounts")
    u = a.setdefault(str(uid), {})
    for p in ("binance", "alpaca"):
        u.setdefault(p, {})["paused"] = bool(paused)
    _save("accounts", a)


# ─── Admin notification (background thread, never blocks) ────────────────────
def notify_admin_async(text):
    def _send():
        try:
            requests.post(
                f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage",
                json={"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown"},
                timeout=5,
            )
        except Exception as e:
            logger.warning(f"admin notify failed: {e}")
    threading.Thread(target=_send, daemon=True).start()


# ─── helpers ─────────────────────────────────────────────────────────────────
def ts_now():
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def date_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def kb(*rows):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t, callback_data=d) for t, d in row] for row in rows
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
    return "🧪 *PRACTICE MODE*"


def fmt_usd(n):
    try:
        return f"${n:,.2f}" if abs(n) >= 1 else f"${n:.4f}"
    except Exception:
        return "$—"


def fmt_pct(n):
    return f"{'+' if n >= 0 else ''}{n:.2f}%"


def pause_icon(uid, platform):
    return "⏸ Paused" if is_paused(uid, platform) else "🟢 Running"


def explain_binance_error(err_str):
    """Convert raw Binance errors into actionable user messages."""
    e = (err_str or "").lower()
    if "-2015" in e or "invalid api-key" in e or "permissions for action" in e:
        return (
            "❌ *Binance Order Failed*\n\n"
            "Your API key cannot place orders. Fix on Binance:\n\n"
            "1️⃣ Enable *Spot & Margin Trading* permission\n"
            "2️⃣ Either *remove IP restriction* OR whitelist:\n"
            "   `72.62.254.237`\n"
            "3️⃣ Make sure the key is not expired (90-day limit)\n"
            "4️⃣ Re-paste the key in Trading → Binance\n\n"
            "_No funds were moved._"
        )
    if "-1021" in e or "timestamp" in e:
        return ("❌ *Binance Order Failed*\n\nServer clock skew.\n"
                "Try again — usually self-resolves.\n\n_No funds moved._")
    if "insufficient balance" in e or "-2010" in e:
        return ("❌ *Insufficient USDT in Binance Spot wallet.*\n\n"
                "Top up your Spot wallet and try again.\n\n_No funds moved._")
    return f"❌ *Order Failed*\n\n`{err_str}`\n\n_No funds moved._"


# ─── SCREEN 1: Trading Home ──────────────────────────────────────────────────
def screen_trading_home(uid):
    bn_line = "├ Binance:      🔗 not connected"
    if has_binance(uid):
        c = get_binance_client(uid)
        if c:
            bn_line = f"├ Binance:      💰 {fmt_usd(c.get_balance('USDT'))} · {pause_icon(uid,'binance')}"

    al_line = "├ Alpaca:       🔗 not connected"
    if has_alpaca(uid):
        c, paper = get_alpaca_client(uid)
        if c:
            tag = "practice" if paper else "live"
            al_line = f"├ Alpaca:       💵 {fmt_usd(c.get_cash())} ({tag}) · {pause_icon(uid,'alpaca')}"

    sl_line = "└ Strategy Lab: 🔗 not loaded"
    if STRATLAB_LOADED:
        try:
            v = oa_value(uid)
            sl_line = f"└ Strategy Lab: 🏛 {fmt_usd(v)} _(practice)_"
        except Exception as e:
            logger.warning(f"strat lab home: {e}")

    trades = get_user_trades(uid)
    open_t = [t for t in trades if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Trading Dashboard*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mode_badge(uid)}\n\n"
        "💼 *Your Accounts*\n"
        f"{bn_line}\n"
        f"{al_line}\n"
        f"{sl_line}\n\n"
        f"📈 Open trades: `{len(open_t)}`\n"
        f"📋 Total:       `{len(trades)} trades`\n\n"
        f"🕐 `{ts_now()}` · `{date_now()}`"
    )
    keyboard = kb(
        [("🤖 Auto Trading",     "td_auto"),   ("✏️ Manual Trade",   "td_manual")],
        [("🏛 Strategy Lab",     "oa_menu"),   ("📈 Market Data",    "td_market")],
        [("📋 Trade History",    "td_history"),("📊 Statistics",     "td_stats")],
        [("⚙️ Bot Settings",      "td_settings"),("🧠 Psychology",     "td_psychology")],
        [("🏠 Main Menu",        "td_mainmenu")],
    )
    return text, keyboard


# ─── Main Menu (bulletproof — uses host's working callbacks) ─────────────────
def screen_mainmenu(uid):
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🏠 *Main Menu*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Where to next?"
    )
    keyboard = kb(
        [("📊 Trading Dashboard", "td_home")],
        [("🤖 Trading Menu",      "trading_menu")],
        [("💰 Balances",          "show_balances"),
         ("📊 Positions",          "show_positions")],
        [("📈 Statistics",         "show_stats"),
         ("📖 User Guide",         "user_guide")],
        [("❓ Help",               "show_help")],
    )
    return text, keyboard


# ─── SCREEN: Auto Trading (rules + pause controls) ───────────────────────────
def screen_auto(uid):
    open_t = [t for t in get_user_trades(uid) if t.get("status") == "OPEN"]
    bn_state = "✅" if has_binance(uid) else "⚠️"
    al_state = "✅" if has_alpaca(uid) else "⚠️"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Auto Trading*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mode_badge(uid)}\n\n"
        "🔗 *Platform status*\n"
        f"├ Binance: {bn_state} · {pause_icon(uid,'binance')}\n"
        f"└ Alpaca:  {al_state} · {pause_icon(uid,'alpaca')}\n\n"
        f"📈 Open positions: `{len(open_t)}`\n\n"
        "🛡 *Safe Default Rules*\n"
        f"├ Risk per trade:  `{RISK_PCT}% of balance`\n"
        f"├ Max per trade:   `${MAX_USD_PER_TRADE}`\n"
        f"├ Stop Loss:       `{STOP_LOSS_PCT}%` ← safety first\n"
        f"├ Take Profit:     `{TAKE_PROFIT_PCT}%`\n"
        f"└ Risk/Reward:     `1:6`\n\n"
        "_Auto execution (background SL/TP) is live on_\n"
        "_Strategy Lab today. Binance/Alpaca auto-engine_\n"
        "_in next phase. Use Manual Trade for now._"
    )
    bn_btn = ("▶️ Resume Binance", "td_resume_binance") if is_paused(uid, "binance") \
             else ("⏸ Pause Binance", "td_pause_binance")
    al_btn = ("▶️ Resume Alpaca", "td_resume_alpaca") if is_paused(uid, "alpaca") \
             else ("⏸ Pause Alpaca", "td_pause_alpaca")

    keyboard = kb(
        [bn_btn, al_btn],
        [("🛑 STOP ALL TRADING", "td_stopall")],
        [("📋 Open Trades", "td_history"), ("📊 Statistics", "td_stats")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN: Manual Trading ──────────────────────────────────────────────────
def screen_manual():
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✏️ *Manual Trading*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔴 *LIVE TRADING* — real money\n"
        "├ Binance:  crypto (BTC, ETH, BNB, SOL)\n"
        "└ Alpaca:   stocks (SPY, QQQ, GLD, USO)\n\n"
        "🏛 *STRATEGY LAB* — practice, $10k balance\n"
        "└ All asset classes, real prices, real SL/TP\n\n"
        "Pick a venue:"
    )
    keyboard = kb(
        [("🔶 Binance — BTC",  "mt_BTCUSD"), ("🔶 Binance — ETH", "mt_ETHUSD")],
        [("🔶 Binance — BNB", "mt_BNBUSD"), ("🔶 Binance — SOL", "mt_SOLUSD")],
        [("📊 Alpaca — SPY",   "mt_SPY"),    ("📊 Alpaca — QQQ",  "mt_QQQ")],
        [("📊 Alpaca — GLD",   "mt_GLD"),    ("📊 Alpaca — USO",  "mt_USO")],
        [("🏛 Open Strategy Lab", "oa_menu")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN: Trade Detail (Binance/Alpaca) ───────────────────────────────────
def screen_trade_detail(symbol, uid):
    cls = asset_class(symbol)
    badge = mode_badge(uid)

    if cls == "crypto":
        if not has_binance(uid):
            return ("🔗 Connect Binance first (Trading Menu → Binance).",
                    kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_manual")]))
        c = get_binance_client(uid)
        if not c:
            return ("⚠️ Binance client error.", kb([("⬅️ Back", "td_manual")]))
        s = c.get_24h_stats(symbol)
        p, hi, lo = fmt_usd(s["price"]), fmt_usd(s["high"]), fmt_usd(s["low"])
        chg = fmt_pct(s["change_pct"])
        arrow = "✅" if s["change_pct"] >= 0 else "❌"
        tag = "🟢 LIVE · Binance"
        usdt = c.get_balance("USDT")
        size = calc_trade_size_usd(usdt)
        paused_note = "\n⏸ _Binance paused — orders blocked_" if is_paused(uid, "binance") else ""

    elif cls == "stock":
        if not has_alpaca(uid):
            return ("🔗 Connect Alpaca first (Trading Menu → Alpaca).",
                    kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_manual")]))
        c, paper = get_alpaca_client(uid)
        if not c:
            return ("⚠️ Alpaca client error.", kb([("⬅️ Back", "td_manual")]))
        price = c.get_price(symbol)
        p = fmt_usd(price) if price else "$—"
        hi = lo = "—"; chg, arrow = "—", "📊"
        tag = f"🟢 LIVE · Alpaca {'(practice)' if paper else '(LIVE)'}"
        cash = c.get_cash()
        size = alpaca_trade_size(cash)
        paused_note = "\n⏸ _Alpaca paused — orders blocked_" if is_paused(uid, "alpaca") else ""
    else:
        return ("⚠️ Unknown symbol.", kb([("⬅️ Back", "td_manual")]))

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{symbol}*  ·  `{tag}`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}{paused_note}\n\n"
        f"💲 Price:    `{p}`\n"
        f"⬆️ 24h High: `{hi}`\n"
        f"⬇️ 24h Low:  `{lo}`\n"
        f"📈 Change:   `{chg}` {arrow}\n\n"
        f"💵 Trade size: `{fmt_usd(size)}` _(1%, capped)_\n\n"
        "🛡 *Safe Rules*\n"
        f"├ Max trade:   `${MAX_USD_PER_TRADE}`\n"
        f"├ Stop Loss:   `−{STOP_LOSS_PCT}%`\n"
        f"└ Take Profit: `+{TAKE_PROFIT_PCT}%`"
    )
    return text, kb(
        [("🟢 BUY", f"exec_buy_{symbol}"), ("🔴 SELL", f"exec_sell_{symbol}")],
        [("⬅️ Back", "td_manual")],
    )


# ─── SCREEN: Market Data ─────────────────────────────────────────────────────
def screen_market(uid):
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

    if has_alpaca(uid):
        c, _ = get_alpaca_client(uid)
        try:
            stocks = (
                "📊 *Stocks* `🟢 LIVE · Alpaca`\n"
                f"├ SPY `{fmt_usd(c.get_price('SPY'))}`\n"
                f"├ QQQ `{fmt_usd(c.get_price('QQQ'))}`\n"
                f"├ GLD `{fmt_usd(c.get_price('GLD'))}`\n"
                f"└ USO `{fmt_usd(c.get_price('USO'))}`\n\n"
            )
        except Exception as e:
            logger.warning(f"stock market: {e}")
            stocks = "📊 *Stocks* `⚠️ market closed / API`\n\n"
    else:
        stocks = "📊 *Stocks* `🔗 Connect Alpaca`\n\n"

    sl = ""
    if STRATLAB_LOADED:
        try:
            sl = ("🏛 *Strategy Lab samples*\n"
                  f"├ Gold  `{fmt_usd(oa_price('GOLD'))}`\n"
                  f"├ EUR/USD `{fmt_usd(oa_price('EURUSD'))}`\n"
                  f"└ S&P 500 `{fmt_usd(oa_price('SP500'))}`\n\n")
        except Exception:
            sl = ""

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 *Market Data*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{crypto}{stocks}{sl}🕐 `{ts_now()}`"
    )
    return text, kb(
        [("🔄 Refresh", "td_market"), ("✏️ Trade Now", "td_manual")],
        [("🏛 Strategy Lab", "oa_menu")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── SCREEN: Trade History ───────────────────────────────────────────────────
def screen_history(uid):
    trades = sorted(get_user_trades(uid), key=lambda x: x.get("created_at", ""), reverse=True)[:6]
    if not trades:
        body = "_No trades yet._\n\nStart with Manual Trade or Strategy Lab."
    else:
        rows = []
        for i, t in enumerate(trades, 1):
            side, sym = t.get("side", "?"), t.get("symbol", "?")
            pnl, mode = t.get("pnl", 0), t.get("mode", "PAPER")
            icon = "✅" if pnl >= 0 else "❌"
            sign = "+" if pnl >= 0 else ""
            tag = {"LIVE": "🔴", "ALPACA": "📊", "PAPER": "🧪", "STRATLAB": "🏛"}.get(mode, "🧪")
            rows.append(f"{i}️⃣ {tag} {sym} · {side} {icon}  `{sign}{pnl:.2f}`")
        body = "\n\n".join(rows)
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Trade History*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}\n\n"
        "_🔴 Binance live · 📊 Alpaca · 🏛 Strategy Lab · 🧪 Practice_"
    )
    return text, kb(
        [("📊 Statistics", "td_stats"), ("🔄 Refresh", "td_history")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── SCREEN: Statistics ──────────────────────────────────────────────────────
def screen_stats(uid):
    trades = get_user_trades(uid)
    total = len(trades)
    wins = sum(1 for t in trades if t.get("pnl", 0) >= 0)
    net = sum(t.get("pnl", 0) for t in trades)
    wr = f"{wins/total*100:.1f}%" if total else "—"
    sign = "+" if net >= 0 else ""
    live = sum(1 for t in trades if t.get("mode") == "LIVE")
    alp = sum(1 for t in trades if t.get("mode") == "ALPACA")
    lab = sum(1 for t in trades if t.get("mode") == "STRATLAB")
    paper = total - live - alp - lab
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Performance Stats*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"├ Total Trades: `{total}`\n"
        f"├ Binance live: `{live}`\n"
        f"├ Alpaca:       `{alp}`\n"
        f"├ Strategy Lab: `{lab}`\n"
        f"├ Practice:     `{paper}`\n"
        f"├ Win Rate:     `{wr}`\n"
        f"└ Net P&L:      `{sign}{net:.2f}`"
    )
    return text, kb(
        [("📋 History", "td_history"), ("🤖 Auto Trading", "td_auto")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── SCREEN: Bot Settings ────────────────────────────────────────────────────
def screen_settings(uid):
    accts = _load("accounts").get(str(uid), {})

    def conn(name):
        a = accts.get(name, {})
        if a.get("status") == "connected": return "🟢 Connected"
        if a.get("status") == "error":     return "🔴 Error"
        if a.get("api_key"):                return "🟡 Unverified"
        return "⬜ Not set"

    live = BINANCE_LOADED and is_live_mode(uid)
    mode_str = "🔴 LIVE (real crypto orders)" if live else "🧪 PRACTICE (safe)"
    toggle = "🧪 Switch to PRACTICE" if live else "🔴 Enable LIVE MODE"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *Bot Settings*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔗 *Exchanges*\n"
        f"├ Binance: `{conn('binance')}`\n"
        f"├ Alpaca:  `{conn('alpaca')}`\n"
        f"├ eToro:   `{conn('etoro')}` _(manual only — no API)_\n"
        f"└ Exness:  `{conn('exness')}` _(needs MT5 — Phase 5)_\n\n"
        "🤖 *Crypto Trading Mode*\n"
        f"└ `{mode_str}`"
    )
    return text, kb(
        [("✅ Verify Binance", "settings_verify")],
        [(toggle, "settings_toggle_mode")],
        [("🔗 Manage APIs", "trading_menu"), ("🔔 Alerts", "settings_notif")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── SCREEN: Trading Psychology ──────────────────────────────────────────────
def screen_psychology():
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *Trading Psychology*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*The 6 Rules of OpenAsset Bot*\n\n"
        "1️⃣ *Risk first, returns second.*\n"
        "   Never risk more than 1% of balance per trade.\n\n"
        "2️⃣ *Cut losses fast.*\n"
        f"   Stop-loss at *{STOP_LOSS_PCT}%* — no exceptions.\n"
        "   Tiny losses compound into nothing.\n\n"
        "3️⃣ *Let winners run.*\n"
        f"   Take-profit at *{TAKE_PROFIT_PCT}%*. Risk/reward = 1:6.\n"
        "   One winner pays for six losers.\n\n"
        "4️⃣ *No revenge trading.*\n"
        "   After a loss, pause. Use the ⏸ button.\n\n"
        "5️⃣ *Position size = math, not feelings.*\n"
        f"   1% risk × max ${MAX_USD_PER_TRADE} live = safe sizing.\n\n"
        "6️⃣ *Practice before you bleed.*\n"
        "   Test every strategy in *Strategy Lab*\n"
        "   before risking real money.\n\n"
        "_Discipline beats prediction. Every time._"
    )
    return text, kb(
        [("🏛 Strategy Lab", "oa_menu"), ("✏️ Manual Trade", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── Verify / Toggle / Live Mode ─────────────────────────────────────────────
def screen_verify(uid):
    if not has_binance(uid):
        return ("⚠️ No Binance API key.", kb([("⬅️ Back", "td_settings")]))
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
        return ("🧪 *Switched to PRACTICE MODE*\n\nNo real crypto orders.",
                kb([("⬅️ Settings", "td_settings")]))
    if not has_binance(uid):
        return ("⚠️ Connect Binance API first.",
                kb([("🔗 Connect", "trading_menu"), ("⬅️ Back", "td_settings")]))
    text = (
        "⚠️ *Enable LIVE MODE?*\n\n"
        "Crypto BUY/SELL will place *REAL orders*.\n\n"
        "🛡 Guards stay on:\n"
        f"├ Max ${MAX_USD_PER_TRADE}/trade\n"
        f"├ {STOP_LOSS_PCT}% SL · {TAKE_PROFIT_PCT}% TP\n"
        "├ BTC/ETH/BNB/SOL only\n"
        "└ No-withdraw key required\n\nSure?"
    )
    return text, kb(
        [("🔴 YES — Enable LIVE", "settings_confirm_live")],
        [("❌ Cancel", "td_settings")],
    )


def screen_confirm_live(uid):
    set_live_mode(uid, True)
    notify_admin_async(f"🔴 User `{uid}` enabled LIVE MODE")
    return ("🔴 *LIVE MODE ENABLED*\n\nReal crypto orders active.",
            kb([("📊 Dashboard", "td_home"), ("⚙️ Settings", "td_settings")]))


# ─── Pause / Resume / Stop-All ───────────────────────────────────────────────
def screen_pause(uid, platform):
    set_paused(uid, platform, True)
    return (f"⏸ *{platform.title()} PAUSED*\n\n"
            "No new orders will be placed on this platform.\n"
            "Existing positions remain open.",
            kb([("▶️ Resume", f"td_resume_{platform}"), ("⬅️ Auto Trading", "td_auto")]))


def screen_resume(uid, platform):
    set_paused(uid, platform, False)
    return (f"▶️ *{platform.title()} RESUMED*\n\nTrading active again.",
            kb([("⬅️ Auto Trading", "td_auto")]))


def screen_stopall(uid):
    set_all_paused(uid, True)
    return ("🛑 *ALL TRADING STOPPED*\n\n"
            "Binance + Alpaca both paused.\n"
            "Existing positions untouched.",
            kb([("▶️ Resume Binance", "td_resume_binance"),
                ("▶️ Resume Alpaca", "td_resume_alpaca")],
               [("⬅️ Dashboard", "td_home")]))


# ─── Binance/Alpaca Confirm ──────────────────────────────────────────────────
def screen_confirm(side, symbol, uid):
    cls = asset_class(symbol)
    platform = "binance" if cls == "crypto" else "alpaca"

    if is_paused(uid, platform):
        return (f"⏸ *{platform.title()} is paused*\n\nResume it first.",
                kb([(f"▶️ Resume {platform.title()}", f"td_resume_{platform}"),
                    ("⬅️ Back", "td_manual")]))

    emoji = "🟢" if side == "buy" else "🔴"
    verb = side.upper()
    if cls == "crypto":
        live = BINANCE_LOADED and is_live_mode(uid) and has_binance(uid)
        badge = "🔴 *LIVE — REAL MONEY*" if live else "🧪 *PRACTICE*"
        venue = "Binance"
    elif cls == "stock":
        badge = "📊 *Alpaca*"
        venue = "Alpaca"
    else:
        badge = "🧪 *PRACTICE*"; venue = "—"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *Confirm {verb}*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{badge}\n\n"
        f"Asset: `{symbol}`\n"
        f"Venue: `{venue}`\n"
        f"Side:  `{verb}`\n"
        f"Type:  `Market`\n\n"
        f"🛡 Rules: SL `{STOP_LOSS_PCT}%` · TP `{TAKE_PROFIT_PCT}%`\n\n"
        "Confirm?"
    )
    return text, kb(
        [(f"✅ Confirm {verb}", f"confirm_{side}_{symbol}"), ("❌ Cancel", "td_manual")],
    )


# ─── Binance/Alpaca Fill ─────────────────────────────────────────────────────
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
    platform = "binance" if cls == "crypto" else "alpaca"

    if is_paused(uid, platform):
        return (f"⏸ *{platform.title()} is paused* — no order placed.",
                kb([(f"▶️ Resume {platform.title()}", f"td_resume_{platform}"),
                    ("⬅️ Back", "td_manual")]))

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
                    return (f"❌ No {asset} in your Binance Spot wallet to sell.",
                            kb([("⬅️ Back", "td_manual")]))
                r = c.place_market_sell(symbol, qty)
            if not r.get("success"):
                return (explain_binance_error(str(r.get("error"))),
                        kb([("📋 History", "td_history"), ("⬅️ Back", "td_manual")]))
            _save_trade(uid, r["symbol"], side, "LIVE",
                        binance_order_id=r["order_id"],
                        entry_price=r["fill_price"], qty=r["qty"],
                        status="OPEN" if side == "buy" else "CLOSED")
            notify_admin_async(
                f"🔴 *LIVE Binance trade*\n"
                f"User: `{uid}`\n{('🟢' if side=='buy' else '🔴')} {side.upper()} `{r['symbol']}`\n"
                f"Fill: {fmt_usd(r['fill_price'])} · Qty: {r['qty']:.6f}"
            )
            return (
                "✅ *LIVE Order Filled!*\n\n"
                f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{r['symbol']}`\n"
                f"Fill: `{fmt_usd(r['fill_price'])}`\n"
                f"Qty:  `{r['qty']:.6f}`\n"
                f"ID:   `{r['order_id']}`\n\n"
                f"🛡 Target SL −{STOP_LOSS_PCT}% / TP +{TAKE_PROFIT_PCT}%",
                kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
            )
        else:
            _save_trade(uid, symbol, side, "PAPER")
            return (
                "✅ *Practice Order Placed*\n\n"
                f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{symbol}`\n"
                "Mode: `Practice (Binance simulation)`\n\n"
                "_Enable Live Mode for real orders, or use Strategy Lab._",
                kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
            )

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
            err = str(r.get("error", ""))
            if "position not found" in err.lower() or "40410000" in err:
                msg = (f"❌ *No {symbol} position to sell.*\n\n"
                       f"You don't currently hold any {symbol}.\n"
                       "Buy it first, then you can sell.")
            elif "market" in err.lower() and "closed" in err.lower():
                msg = ("❌ *US market is closed.*\n\n"
                       "Stocks trade 9:30am–4pm ET, Mon–Fri.")
            else:
                msg = f"❌ *Alpaca Order Failed*\n\n`{err}`"
            return (msg, kb([("📋 History", "td_history"), ("⬅️ Back", "td_manual")]))
        _save_trade(uid, r["symbol"], side, "ALPACA",
                    alpaca_order_id=r.get("order_id"),
                    entry_price=r.get("fill_price", 0), qty=r.get("qty", 0),
                    status="OPEN" if side == "buy" else "CLOSED")
        if not paper:
            notify_admin_async(
                f"🔴 *LIVE Alpaca trade*\nUser: `{uid}`\n"
                f"{('🟢' if side=='buy' else '🔴')} {side.upper()} `{r['symbol']}`"
            )
        return (
            f"✅ *Alpaca Order Placed* {'(practice)' if paper else '(LIVE)'}\n\n"
            f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{r['symbol']}`\n"
            f"Order ID: `{r.get('order_id','—')}`\n"
            f"Time: `{ts_now()}`\n\n"
            f"🛡 Target SL −{STOP_LOSS_PCT}% / TP +{TAKE_PROFIT_PCT}%",
            kb([("📋 History", "td_history"), ("🏠 Dashboard", "td_home")]),
        )
    else:
        return ("⚠️ Unknown symbol.", kb([("⬅️ Back", "td_manual")]))


# ─── STRATEGY LAB SCREENS ────────────────────────────────────────────────────
def screen_oa_menu(uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded. Run installer.",
                kb([("⬅️ Back", "td_home")]))

    cash = oa_cash(uid)
    value = oa_value(uid)
    unreal = oa_unrealized(uid)
    open_pos = oa_positions(uid)
    sign = "+" if unreal >= 0 else ""

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🏛 *Strategy Lab*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Practice with real prices, $10k balance,_\n"
        "_real SL/TP. Perfect for testing strategy_\n"
        "_before you risk real money._\n\n"
        f"💵 Cash:           `{fmt_usd(cash)}`\n"
        f"📊 Portfolio:      `{fmt_usd(value)}`\n"
        f"📈 Unrealized P&L: `{sign}{unreal:.2f}`\n"
        f"📋 Open positions: `{len(open_pos)}`\n\n"
        "*Pick an asset class:*"
    )
    rows = []
    classes = oa_list_classes()
    # 2 per row
    for i in range(0, len(classes), 2):
        row = []
        for c in classes[i:i+2]:
            row.append((f"{OA_CLASS_EMOJI.get(c,'•')} {OA_CLASS_LABEL.get(c,c)}", f"oa_c_{c}"))
        rows.append(row)
    rows.append([("📊 My Portfolio", "oa_acct"), ("🔄 Reset", "oa_reset")])
    rows.append([("⬅️ Dashboard", "td_home")])
    return text, kb(*rows)


def screen_oa_class(asset_class_name, uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded.", kb([("⬅️ Back", "td_home")]))
    symbols = oa_list_symbols(asset_class_name)
    if not symbols:
        return (f"No symbols in {asset_class_name}.",
                kb([("⬅️ Back", "oa_menu")]))
    emoji = OA_CLASS_EMOJI.get(asset_class_name, "•")
    label = OA_CLASS_LABEL.get(asset_class_name, asset_class_name)
    status = oa_market_status(asset_class_name)
    if status["is_open"]:
        market_line = f"🟢 *{status['market_name']}* — open\n"
    else:
        tu = oa_fmt_time(status["opens_in_minutes"])
        market_line = (f"🔴 *{status['market_name']}* — closed\n"
                       f"   opens in `{tu}` ({status['opens_at_str']})\n")
    text = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *{label}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{market_line}\n"
        f"Pick a symbol to view:"
    )
    rows = []
    for i in range(0, len(symbols), 2):
        row = []
        for s in symbols[i:i+2]:
            name = oa_display(s)
            row.append((f"{s} · {name}", f"oa_v_{s}"))
        rows.append(row)
    rows.append([("⬅️ Strategy Lab", "oa_menu")])
    return text, kb(*rows)


def screen_oa_view(symbol, uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded.", kb([("⬅️ Back", "td_home")]))
    cls = oa_class_of(symbol)
    if not cls:
        return (f"⚠️ Unknown symbol {symbol}.", kb([("⬅️ Back", "oa_menu")]))
    price = oa_price(symbol)
    name = oa_display(symbol)
    emoji = OA_CLASS_EMOJI.get(cls, "•")
    cash = oa_cash(uid)
    pos = oa_get_pos(uid, symbol)

    # Market status — shown upfront so user knows before tapping BUY
    status = oa_market_status(cls)
    if status["is_open"]:
        market_line = f"🟢 *{status['market_name']}* — open"
    else:
        tu = oa_fmt_time(status["opens_in_minutes"])
        market_line = (f"🔴 *{status['market_name']}* — closed\n"
                       f"   opens in `{tu}` ({status['opens_at_str']})")

    price_line = f"💲 Price: `{fmt_usd(price)}`" if price > 0 \
                 else f"💲 Price: `—` _(unavailable while closed)_"

    pos_block = ""
    if pos:
        ref_price = price if price > 0 else pos["avg_entry"]
        cur_value = pos["qty"] * ref_price
        cost = pos["qty"] * pos["avg_entry"]
        pnl = cur_value - cost
        sign = "+" if pnl >= 0 else ""
        pos_block = (
            f"\n📌 *You hold this:*\n"
            f"├ Qty:      `{pos['qty']:.6f}`\n"
            f"├ Avg entry:`{fmt_usd(pos['avg_entry'])}`\n"
            f"├ Value:    `{fmt_usd(cur_value)}`\n"
            f"└ P&L:      `{sign}{pnl:.2f}`\n"
        )

    text = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *{symbol}* · _{name}_\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{market_line}\n\n"
        f"{price_line}\n"
        f"💵 Your cash: `{fmt_usd(cash)}`\n"
        f"{pos_block}\n"
        "🛡 *Order defaults*\n"
        f"├ Trade size: `$50` _(practice)_\n"
        f"├ Stop Loss:  `−{STOP_LOSS_PCT}%`\n"
        f"└ Take Profit:`+{TAKE_PROFIT_PCT}%`"
    )
    rows = []
    if status["is_open"] and price > 0:
        rows.append([("🟢 BUY $50", f"oa_b_{symbol}")])
    else:
        rows.append([("⏳ Market Closed", f"oa_v_{symbol}")])  # tappable refresh
    if pos:
        # Allow closing positions even when market closed (uses last-known price)
        rows.append([("🔴 Close Position", f"oa_s_{symbol}")])
    rows.append([("🔄 Refresh", f"oa_v_{symbol}"), ("⬅️ Back", f"oa_c_{cls}")])
    return text, kb(*rows)


def screen_oa_confirm(side, symbol, uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded.", kb([("⬅️ Back", "td_home")]))
    price = oa_price(symbol)
    emoji = "🟢" if side == "buy" else "🔴"
    verb = "BUY" if side == "buy" else "CLOSE"
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *Confirm {verb} (Strategy Lab)*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏛 *Practice — no real money*\n\n"
        f"Asset: `{symbol}` · _{oa_display(symbol)}_\n"
        f"Price: `{fmt_usd(price)}`\n"
        f"Side:  `{verb}`\n"
        f"Size:  `$50` _(notional)_\n\n"
        f"🛡 Auto SL `−{STOP_LOSS_PCT}%` · TP `+{TAKE_PROFIT_PCT}%`\n\n"
        "Confirm?"
    )
    fill_cb = f"oa_fb_{symbol}" if side == "buy" else f"oa_fs_{symbol}"
    return text, kb(
        [(f"✅ Confirm {verb}", fill_cb), ("❌ Cancel", f"oa_v_{symbol}")],
    )


def screen_oa_fill(side, symbol, uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded.", kb([("⬅️ Back", "td_home")]))
    if side == "buy":
        r = oa_buy(uid, symbol, 50.0)
        if not r.get("success"):
            return (f"❌ *Order Failed*\n\n`{r.get('error')}`",
                    kb([("⬅️ Back", f"oa_v_{symbol}")]))
        # Auto-set SL/TP
        oa_set_sl_tp(uid, symbol, STOP_LOSS_PCT, TAKE_PROFIT_PCT)
        _save_trade(uid, symbol, "buy", "STRATLAB",
                    oa_order_id=r["order_id"], entry_price=r["fill_price"],
                    qty=r["qty"], status="OPEN")
        return (
            f"✅ *Strategy Lab BUY Filled*\n\n"
            f"🟢 BUY `{symbol}`\n"
            f"Fill: `{fmt_usd(r['fill_price'])}`\n"
            f"Qty:  `{r['qty']:.6f}`\n"
            f"Cost: `${r['usd_spent']:.2f}`\n\n"
            f"🛡 SL/TP active: −{STOP_LOSS_PCT}% / +{TAKE_PROFIT_PCT}%\n"
            f"_Background monitor auto-closes when hit._",
            kb([("📊 My Portfolio", "oa_acct"),
                ("🏛 Strategy Lab",  "oa_menu")],
               [("🏠 Dashboard", "td_home")])
        )
    else:
        r = oa_close(uid, symbol, reason="MANUAL")
        if not r.get("success"):
            return (f"❌ *Close Failed*\n\n`{r.get('error')}`",
                    kb([("⬅️ Back", f"oa_v_{symbol}")]))
        _save_trade(uid, symbol, "sell", "STRATLAB",
                    oa_order_id=f"close_{int(datetime.now(timezone.utc).timestamp())}",
                    entry_price=r["fill_price"], qty=r["qty"],
                    pnl=r["pnl"], status="CLOSED")
        sign = "+" if r["pnl"] >= 0 else ""
        emoji = "✅" if r["pnl"] >= 0 else "❌"
        return (
            f"{emoji} *Position Closed*\n\n"
            f"🔴 SELL `{symbol}`\n"
            f"Fill: `{fmt_usd(r['fill_price'])}`\n"
            f"P&L:  `{sign}{r['pnl']:.2f}`\n",
            kb([("📊 My Portfolio", "oa_acct"),
                ("🏛 Strategy Lab",  "oa_menu")],
               [("🏠 Dashboard", "td_home")])
        )


def screen_oa_account(uid):
    if not STRATLAB_LOADED:
        return ("⚠️ Strategy Lab not loaded.", kb([("⬅️ Back", "td_home")]))
    cash = oa_cash(uid)
    value = oa_value(uid)
    unreal = oa_unrealized(uid)
    positions = oa_positions(uid)
    sign = "+" if unreal >= 0 else ""

    if not positions:
        pos_block = "_No open positions._\nStart by picking an asset class."
    else:
        rows = []
        for sym, p in positions.items():
            cur_price = oa_price(sym)
            cur_val = p["qty"] * cur_price
            pnl = (cur_price - p["avg_entry"]) * p["qty"]
            s = "+" if pnl >= 0 else ""
            icon = "🟢" if pnl >= 0 else "🔴"
            rows.append(
                f"{icon} `{sym}` · qty `{p['qty']:.4f}`\n"
                f"   entry `{fmt_usd(p['avg_entry'])}` · now `{fmt_usd(cur_price)}`\n"
                f"   P&L `{s}{pnl:.2f}`"
            )
        pos_block = "\n\n".join(rows)

    trades = oa_trades_fn(uid, limit=3)
    history = ""
    if trades:
        rows = []
        for t in trades:
            s = "+" if t.get("pnl", 0) >= 0 else ""
            r = t.get("reason", "")
            rows.append(f"• `{t['symbol']}` · {t['side']} `{s}{t['pnl']:.2f}` _{r}_")
        history = "\n\n*Recent closed:*\n" + "\n".join(rows)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🏛 *Strategy Lab Portfolio*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💵 Cash:           `{fmt_usd(cash)}`\n"
        f"📊 Portfolio val:  `{fmt_usd(value)}`\n"
        f"📈 Unrealized P&L: `{sign}{unreal:.2f}`\n"
        f"📋 Positions:      `{len(positions)}`\n\n"
        f"*Open positions:*\n{pos_block}"
        f"{history}"
    )
    return text, kb(
        [("🔄 Refresh", "oa_acct"), ("🏛 Trade More", "oa_menu")],
        [("⬅️ Dashboard", "td_home")],
    )


def screen_oa_reset_confirm():
    text = (
        "🔄 *Reset Strategy Lab?*\n\n"
        f"This will wipe your practice positions and\n"
        f"restore your cash to `${OA_START:,.0f}`.\n\n"
        "Trade history is kept.\n\n"
        "Are you sure?"
    )
    return text, kb(
        [("🔄 YES — Reset to $10k", "oa_reset_y")],
        [("❌ Cancel", "oa_menu")],
    )


def screen_oa_reset_do(uid):
    oa_reset_acct(uid)
    return (
        f"✅ *Strategy Lab reset.*\n\n"
        f"Cash restored to `${OA_START:,.0f}`.\n"
        "Time to test a new strategy.",
        kb([("🏛 Strategy Lab", "oa_menu"), ("🏠 Dashboard", "td_home")]),
    )


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

    # Universal back_home intercept — fixes Help/FAQ/Guide back buttons
    if data == "back_home":
        text, keyboard = screen_mainmenu(uid)

    # Core dashboard screens
    elif data == "td_home":       text, keyboard = screen_trading_home(uid)
    elif data == "td_mainmenu":   text, keyboard = screen_mainmenu(uid)
    elif data == "td_auto":       text, keyboard = screen_auto(uid)
    elif data == "td_manual":     text, keyboard = screen_manual()
    elif data == "td_market":     text, keyboard = screen_market(uid)
    elif data == "td_history":    text, keyboard = screen_history(uid)
    elif data == "td_stats":      text, keyboard = screen_stats(uid)
    elif data == "td_settings":   text, keyboard = screen_settings(uid)
    elif data == "td_psychology": text, keyboard = screen_psychology()

    # Pause / resume / stop
    elif data == "td_pause_binance":  text, keyboard = screen_pause(uid, "binance")
    elif data == "td_pause_alpaca":   text, keyboard = screen_pause(uid, "alpaca")
    elif data == "td_resume_binance": text, keyboard = screen_resume(uid, "binance")
    elif data == "td_resume_alpaca":  text, keyboard = screen_resume(uid, "alpaca")
    elif data == "td_stopall":        text, keyboard = screen_stopall(uid)

    # Settings actions
    elif data == "settings_verify":       text, keyboard = screen_verify(uid)
    elif data == "settings_toggle_mode":  text, keyboard = screen_toggle_mode(uid)
    elif data == "settings_confirm_live": text, keyboard = screen_confirm_live(uid)
    elif data == "settings_notif":
        text = "🔔 *Notifications*\n\n✅ All alerts active."
        keyboard = kb([("⬅️ Settings", "td_settings")])

    # Binance/Alpaca order flow
    elif data.startswith("mt_"):           text, keyboard = screen_trade_detail(data[3:], uid)
    elif data.startswith("exec_buy_"):     text, keyboard = screen_confirm("buy", data[9:], uid)
    elif data.startswith("exec_sell_"):    text, keyboard = screen_confirm("sell", data[10:], uid)
    elif data.startswith("confirm_buy_"):  text, keyboard = screen_filled("buy", data[12:], uid)
    elif data.startswith("confirm_sell_"): text, keyboard = screen_filled("sell", data[13:], uid)

    # Strategy Lab
    elif data == "oa_menu":     text, keyboard = screen_oa_menu(uid)
    elif data == "oa_acct":     text, keyboard = screen_oa_account(uid)
    elif data == "oa_reset":    text, keyboard = screen_oa_reset_confirm()
    elif data == "oa_reset_y":  text, keyboard = screen_oa_reset_do(uid)
    elif data.startswith("oa_c_"):  text, keyboard = screen_oa_class(data[5:], uid)
    elif data.startswith("oa_v_"):  text, keyboard = screen_oa_view(data[5:], uid)
    elif data.startswith("oa_b_"):  text, keyboard = screen_oa_confirm("buy", data[5:], uid)
    elif data.startswith("oa_s_"):  text, keyboard = screen_oa_confirm("sell", data[5:], uid)
    elif data.startswith("oa_fb_"): text, keyboard = screen_oa_fill("buy", data[6:], uid)
    elif data.startswith("oa_fs_"): text, keyboard = screen_oa_fill("sell", data[6:], uid)

    if text is None:
        return  # not ours

    try:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.warning(f"edit failed: {e}")
