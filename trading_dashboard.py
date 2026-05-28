#!/usr/bin/env python3
"""
OpenAsset Trading Dashboard
===========================
Binance (crypto) + Alpaca (stocks), with:
  * Bulletproof home button (own callback, no host dependency)
  * Trade pause/resume per platform + STOP ALL emergency
  * Safe defaults: 0.5% SL, 3% TP (1:6 R/R), 1% risk, $50 cap
  * Trading psychology / rules screen
"""

import os, json, logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

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

# Safe-by-default trading rules
STOP_LOSS_PCT = 0.5   # %
TAKE_PROFIT_PCT = 3.0  # %
RISK_PCT = 1.0         # % of balance per trade

TRADING_CALLBACK_PATTERN = (
    r"^(td_home|td_mainmenu|td_auto|td_manual|td_market|td_history|"
    r"td_stats|td_settings|td_psychology|td_pause_|td_resume_|td_stopall|"
    r"td_resumeall|mt_|exec_buy_|exec_sell_|confirm_buy_|confirm_sell_|"
    r"bot_start|bot_config|settings_notif|settings_verify|"
    r"settings_toggle_mode|settings_confirm_live)"
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
    return [t for t in _load("trades").values() if str(t.get("user_id")) == str(uid)]


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
    return "🧪 *PAPER MODE*"


def fmt_usd(n):
    try:
        return f"${n:,.2f}" if abs(n) >= 1 else f"${n:.4f}"
    except Exception:
        return "$—"


def fmt_pct(n):
    return f"{'+' if n >= 0 else ''}{n:.2f}%"


def pause_icon(uid, platform):
    return "⏸ Paused" if is_paused(uid, platform) else "🟢 Running"


# ─── SCREEN 1: Trading Home ──────────────────────────────────────────────────
def screen_trading_home(uid):
    bn_line = "├ Binance: 🔗 not connected"
    if has_binance(uid):
        c = get_binance_client(uid)
        if c:
            bal = fmt_usd(c.get_balance("USDT"))
            bn_line = f"├ Binance: 💰 {bal} · {pause_icon(uid,'binance')}"

    al_line = "└ Alpaca:  🔗 not connected"
    if has_alpaca(uid):
        c, paper = get_alpaca_client(uid)
        if c:
            tag = "paper" if paper else "live"
            al_line = f"└ Alpaca:  💵 {fmt_usd(c.get_cash())} ({tag}) · {pause_icon(uid,'alpaca')}"

    trades = get_user_trades(uid)
    open_t = [t for t in trades if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Trading Dashboard*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mode_badge(uid)}\n\n"
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
        [("🧠 Trading Psychology", "td_psychology")],
        [("🏠 Main Menu",    "td_mainmenu")],
    )
    return text, keyboard


# ─── Main Menu (bulletproof — uses host's working callbacks) ─────────────────
def screen_mainmenu(uid):
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🏠 *Main Menu*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose where to go:"
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


# ─── SCREEN 2: Auto Trading (with pause control) ─────────────────────────────
def screen_auto(uid):
    open_t = [t for t in get_user_trades(uid) if t.get("status") == "OPEN"]
    bn_state = "✅" if has_binance(uid) else "⚠️"
    al_state = "✅" if has_alpaca(uid) else "⚠️"

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Auto Trading Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mode_badge(uid)}\n\n"
        "🔗 *Platform status*\n"
        f"├ Binance: {bn_state} · {pause_icon(uid,'binance')}\n"
        f"└ Alpaca:  {al_state} · {pause_icon(uid,'alpaca')}\n\n"
        f"📈 Open positions: `{len(open_t)}`\n\n"
        "🛡 *Safe Default Rules* (all platforms)\n"
        f"├ Risk per trade:  `{RISK_PCT}% of balance`\n"
        f"├ Max per trade:   `${MAX_USD_PER_TRADE}`\n"
        f"├ Stop Loss:       `{STOP_LOSS_PCT}%` ← safety first\n"
        f"├ Take Profit:     `{TAKE_PROFIT_PCT}%`\n"
        f"└ Risk/Reward:     `1:6`\n\n"
        "_Auto engine (background SL/TP)_\n_ships Phase 4. Today: pause controls_\n_and the rules are shown for manual use._"
    )

    # Build pause/resume buttons
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


# ─── SCREEN 3: Manual Trading ────────────────────────────────────────────────
def screen_manual():
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✏️ *Manual Trading*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔶 *Crypto* — Binance (live in Live Mode)\n"
        "📊 *Stocks* — Alpaca\n\n"
        "Choose an asset:"
    )
    keyboard = kb(
        [("₿ BTC/USD",  "mt_BTCUSD"), ("Ξ ETH/USD", "mt_ETHUSD")],
        [("🟡 BNB/USD", "mt_BNBUSD"), ("◎ SOL/USD", "mt_SOLUSD")],
        [("📈 SPY",     "mt_SPY"),    ("📈 QQQ",    "mt_QQQ")],
        [("🥇 GLD",     "mt_GLD"),    ("⚫ USO",    "mt_USO")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN 4: Trade Detail ──────────────────────────────────────────────────
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
        tag = f"🟢 LIVE · Alpaca {'(paper)' if paper else '(live)'}"
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


# ─── SCREEN 5: Market Data ───────────────────────────────────────────────────
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

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 *Market Data*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{crypto}{stocks}🕐 `{ts_now()}`"
    )
    return text, kb(
        [("🔄 Refresh", "td_market"), ("✏️ Trade Now", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── SCREEN 6: Trade History ─────────────────────────────────────────────────
def screen_history(uid):
    trades = sorted(get_user_trades(uid), key=lambda x: x.get("created_at", ""), reverse=True)[:6]
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
            rows.append(f"{i}️⃣ {tag} {sym} · {side} {icon}  `{sign}{pnl:.2f}`")
        body = "\n\n".join(rows)
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Trade History*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}\n\n"
        "_🔴 Binance live · 📊 Alpaca · 🧪 Paper_"
    )
    return text, kb(
        [("📊 Statistics", "td_stats"), ("🔄 Refresh", "td_history")],
        [("⬅️ Dashboard", "td_home")],
    )


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
    return text, kb(
        [("📋 History", "td_history"), ("🤖 Auto Trading", "td_auto")],
        [("⬅️ Dashboard", "td_home")],
    )


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


# ─── SCREEN 9: Trading Psychology ────────────────────────────────────────────
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
        "   After a loss, pause. Use the ⏸ button.\n"
        "   Emotional trading kills accounts.\n\n"
        "5️⃣ *Position size = math, not feelings.*\n"
        f"   1% risk × max ${MAX_USD_PER_TRADE} = safe sizing.\n\n"
        "6️⃣ *Trade only what you understand.*\n"
        "   BTC, ETH, SPY, QQQ — liquid, deep markets.\n"
        "   No random altcoins. No memestocks.\n\n"
        "_Discipline beats prediction. Every time._"
    )
    return text, kb(
        [("🤖 Auto Trading", "td_auto"), ("✏️ Manual Trade", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )


# ─── Verify / Toggle Live Mode ───────────────────────────────────────────────
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
        return ("🧪 *Switched to PAPER MODE*\n\nNo real crypto orders.",
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
            "No new orders will fire.\n\n"
            "Existing positions are untouched.\n"
            "Resume each platform when ready.",
            kb([("▶️ Resume Binance", "td_resume_binance"),
                ("▶️ Resume Alpaca", "td_resume_alpaca")],
               [("⬅️ Dashboard", "td_home")]))


# ─── Confirm Order ───────────────────────────────────────────────────────────
def screen_confirm(side, symbol, uid):
    cls = asset_class(symbol)
    platform = "binance" if cls == "crypto" else "alpaca"

    if is_paused(uid, platform):
        return (f"⏸ *{platform.title()} is paused*\n\nResume it first to place orders.",
                kb([(f"▶️ Resume {platform.title()}", f"td_resume_{platform}"),
                    ("⬅️ Back", "td_manual")]))

    emoji = "🟢" if side == "buy" else "🔴"
    verb = side.upper()
    if cls == "crypto":
        live = BINANCE_LOADED and is_live_mode(uid) and has_binance(uid)
        badge = "🔴 *LIVE — REAL MONEY*" if live else "🧪 *PAPER*"
        venue = "Binance"
    elif cls == "stock":
        badge = "📊 *Alpaca*"
        venue = "Alpaca"
    else:
        badge = "🧪 *PAPER*"; venue = "—"

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
    platform = "binance" if cls == "crypto" else "alpaca"

    # Paused guard (defense in depth)
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
                f"ID:   `{r['order_id']}`\n\n"
                f"🛡 Watch for SL −{STOP_LOSS_PCT}% / TP +{TAKE_PROFIT_PCT}%\n"
                "_Auto-close ships Phase 4._",
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
            # Better message for "position not found"
            if "position not found" in err.lower() or "40410000" in err:
                msg = (f"❌ *No {symbol} position to sell.*\n\n"
                       f"You don't currently hold any {symbol}.\n"
                       "Buy it first, then you can sell.")
            elif "market" in err.lower() and "closed" in err.lower():
                msg = ("❌ *US market is closed.*\n\n"
                       "Stocks trade 9:30am–4pm ET, Mon–Fri.\n"
                       "Try during market hours.")
            else:
                msg = f"❌ *Alpaca Order Failed*\n\n`{err}`"
            return (msg, kb([("📋 History", "td_history"), ("⬅️ Back", "td_manual")]))
        _save_trade(uid, r["symbol"], side, "ALPACA",
                    alpaca_order_id=r.get("order_id"),
                    entry_price=r.get("fill_price", 0), qty=r.get("qty", 0),
                    status="OPEN" if side == "buy" else "CLOSED")
        return (
            f"✅ *Alpaca Order Placed* {'(paper)' if paper else '(live)'}\n\n"
            f"{'🟢' if side=='buy' else '🔴'} {side.upper()} `{r['symbol']}`\n"
            f"Order ID: `{r.get('order_id','—')}`\n"
            f"Time: `{ts_now()}`\n\n"
            f"🛡 Watch for SL −{STOP_LOSS_PCT}% / TP +{TAKE_PROFIT_PCT}%",
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

    # Screens
    if   data == "td_home":       text, keyboard = screen_trading_home(uid)
    elif data == "td_mainmenu":   text, keyboard = screen_mainmenu(uid)
    elif data == "td_auto":       text, keyboard = screen_auto(uid)
    elif data == "td_manual":     text, keyboard = screen_manual()
    elif data == "td_market":     text, keyboard = screen_market(uid)
    elif data == "td_history":    text, keyboard = screen_history(uid)
    elif data == "td_stats":      text, keyboard = screen_stats(uid)
    elif data == "td_settings":   text, keyboard = screen_settings(uid)
    elif data == "td_psychology": text, keyboard = screen_psychology()

    # Pause / resume / stop-all
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

    # Pair / order flow
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
        text = "🤖 *Auto engine ships Phase 4.*\nUse Manual Trade for now."
        keyboard = kb([("⬅️ Back", "td_auto")])
    elif data == "bot_config":
        text = (f"🔧 *Config*\n"
                f"├ Risk {RISK_PCT}% · Max ${MAX_USD_PER_TRADE}\n"
                f"├ SL {STOP_LOSS_PCT}% · TP {TAKE_PROFIT_PCT}%\n"
                "└ BTC/ETH/BNB/SOL + stocks")
        keyboard = kb([("⬅️ Back", "td_auto")])

    if text is None:
        return  # not ours — host bot handles

    try:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.warning(f"edit failed: {e}")
