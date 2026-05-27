#!/usr/bin/env python3
"""
OpenAsset Trading Dashboard Module
===================================
Integrates with main.py via the /trading command.

Provides 8 screens:
  1. Trading Home    (td_home)
  2. Auto Trading    (td_auto)
  3. Manual Trade    (td_manual)
  4. Trade Detail    (mt_<symbol>)
  5. Market Data     (td_market)
  6. Trade History   (td_history)
  7. Statistics      (td_stats)
  8. Bot Settings    (td_settings)

Plus confirm/filled flow for manual orders.

Usage in main.py:
    from trading_dashboard import (
        cmd_trading_dashboard,
        handle_trading_callbacks,
        TRADING_CALLBACK_PATTERN,
    )

    app.add_handler(CommandHandler("trading", cmd_trading_dashboard))
    app.add_handler(CallbackQueryHandler(
        handle_trading_callbacks,
        pattern=TRADING_CALLBACK_PATTERN,
    ))
"""

import os
import json
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────────────────
ADMIN_ID = 5587885687
DB_PATH = "/root/openasset_club/telegram_bot/database"

# Callback pattern - only these prefixes will be routed to this module
TRADING_CALLBACK_PATTERN = (
    r"^(td_home|td_auto|td_manual|td_market|td_history|"
    r"td_stats|td_settings|mt_|exec_buy_|exec_sell_|"
    r"confirm_buy_|confirm_sell_|bot_start|bot_config|settings_notif)"
)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _load(name: str) -> dict:
    """Load JSON database file."""
    try:
        with open(f"{DB_PATH}/{name}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(name: str, data: dict) -> None:
    """Save JSON database file."""
    os.makedirs(DB_PATH, exist_ok=True)
    with open(f"{DB_PATH}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)


def ts_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def date_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_user_accounts(uid: str) -> dict:
    return _load("accounts").get(str(uid), {})


def get_user_trades(uid: str) -> list:
    trades = _load("trades")
    return [t for t in trades.values() if str(t.get("user_id")) == str(uid)]


def kb(*rows) -> InlineKeyboardMarkup:
    """Build an inline keyboard from rows of (text, callback_data) tuples."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in rows
    ])


# ─── DEMO PRICES (replace with live feed in Phase 4) ─────────────────────────
PRICES = {
    "BTCUSD": ("$67,432", "$68,100", "$66,890", "+1.42%", True),
    "ETHUSD": ("$3,521",  "$3,580",  "$3,480",  "+0.87%", True),
    "SPY":    ("$521.44", "$523.10", "$519.80", "+0.31%", True),
    "QQQ":    ("$442.10", "$445.00", "$440.20", "+0.52%", True),
    "GLD":    ("$231.75", "$232.50", "$230.80", "+0.18%", True),
    "USO":    ("$74.20",  "$75.10",  "$73.80",  "+0.54%", True),
}


# ─── SCREEN 1: Trading Home ──────────────────────────────────────────────────
def screen_trading_home(uid: str):
    accts = get_user_accounts(uid)
    connected = sum(1 for k in accts.values()
                    if isinstance(k, dict) and k.get("status") == "connected")
    trades = get_user_trades(uid)
    open_t = [t for t in trades if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Trading Dashboard*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 Exchanges:   `{connected}/4 connected`\n"
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
def screen_auto(uid: str):
    accts = get_user_accounts(uid)
    binance_ok = accts.get("binance", {}).get("status") == "connected"
    open_t = [t for t in get_user_trades(uid) if t.get("status") == "OPEN"]

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Auto Trading Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Exchange: `{'Binance ✅' if binance_ok else '⚠️ Connect first'}`\n"
        f"Status:   `⬜ Standby`\n"
        f"Open:     `{len(open_t)} positions`\n\n"
        "⚙️ *Default Settings*\n"
        "├ Risk/Trade: `1% of balance`\n"
        "├ Stop Loss:  `2%`\n"
        "├ Take Profit:`3%`\n"
        "└ Strategy:   `Trend following`\n\n"
        "⚠️ *Paper Trading Mode Active*\n"
        "_No real money will be used until_\n"
        "_you switch to Live mode in settings._"
    )
    keyboard = kb(
        [("▶️ Start Bot",   "bot_start"),  ("🔧 Configure",  "bot_config")],
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
        "Choose an asset to trade:"
    )
    keyboard = kb(
        [("₿ BTC/USD", "mt_BTCUSD"), ("Ξ ETH/USD", "mt_ETHUSD")],
        [("📈 SPY",     "mt_SPY"),    ("📈 QQQ",     "mt_QQQ")],
        [("🥇 GLD",     "mt_GLD"),    ("⚫ USO",     "mt_USO")],
        [("⬅️ Dashboard","td_home")],
    )
    return text, keyboard


# ─── SCREEN 4: Trade Detail ──────────────────────────────────────────────────
def screen_trade_detail(symbol: str):
    p, hi, lo, chg, up = PRICES.get(symbol, ("—", "—", "—", "—", True))
    arrow = "✅" if up else "❌"
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{symbol}*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💲 Price:     `{p}`\n"
        f"⬆️  24h High: `{hi}`\n"
        f"⬇️  24h Low:  `{lo}`\n"
        f"📈 Change:    `{chg}` {arrow}\n\n"
        "🛡 *Risk Settings*\n"
        "├ Risk:        `1% of balance`\n"
        "├ Stop Loss:   `−2%`\n"
        "└ Take Profit: `+3%`\n\n"
        "⚠️ Paper Trade — no real funds."
    )
    keyboard = kb(
        [("🟢 BUY", f"exec_buy_{symbol}"), ("🔴 SELL", f"exec_sell_{symbol}")],
        [("⬅️ Back", "td_manual")],
    )
    return text, keyboard


# ─── SCREEN 5: Market Data ───────────────────────────────────────────────────
def screen_market():
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 *Live Market Data*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔶 *Crypto*\n"
        "├ ₿  BTC   `$67,432`  `+1.42%` ✅\n"
        "├ Ξ  ETH   `$3,521`   `+0.87%` ✅\n"
        "├ BNB      `$612`     `+2.11%` ✅\n"
        "└ SOL      `$178`     `−0.34%` ❌\n\n"
        "📊 *Stocks / ETFs*\n"
        "├ SPY      `$521.44`  `+0.31%` ✅\n"
        "├ QQQ      `$442.10`  `+0.52%` ✅\n"
        "├ IWM      `$201.30`  `−0.12%` ❌\n"
        "└ DIA      `$389.20`  `+0.08%` ✅\n\n"
        "🏅 *Commodities*\n"
        "├ GLD      `$231.75`  `+0.18%` ✅\n"
        "└ USO      `$74.20`   `+0.54%` ✅\n\n"
        f"🕐 `{ts_now()}`  _(simulated)_"
    )
    keyboard = kb(
        [("🔄 Refresh",   "td_market"), ("✏️ Trade Now", "td_manual")],
        [("⬅️ Dashboard", "td_home")],
    )
    return text, keyboard


# ─── SCREEN 6: Trade History ─────────────────────────────────────────────────
def screen_history(uid: str):
    trades = sorted(
        get_user_trades(uid),
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )[:5]

    if not trades:
        body = "_No trades recorded yet._\n\nStart with Auto or Manual trading."
    else:
        rows = []
        for i, t in enumerate(trades, 1):
            side = t.get("side", "?")
            sym = t.get("symbol", "?")
            pnl = t.get("pnl", 0)
            icon = "✅" if pnl >= 0 else "❌"
            sign = "+" if pnl >= 0 else ""
            rows.append(f"{i}️⃣  {sym} · {side} {icon}  `{sign}{pnl:.2f}`")
        body = "\n\n".join(rows)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Trade History*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}"
    )
    keyboard = kb(
        [("📊 Statistics", "td_stats"), ("🔄 Refresh", "td_history")],
        [("⬅️ Dashboard",  "td_home")],
    )
    return text, keyboard


# ─── SCREEN 7: Statistics ────────────────────────────────────────────────────
def screen_stats(uid: str):
    trades = get_user_trades(uid)
    total = len(trades)
    wins = sum(1 for t in trades if t.get("pnl", 0) >= 0)
    losses = total - wins
    net_pnl = sum(t.get("pnl", 0) for t in trades)
    wr = f"{wins / total * 100:.1f}%" if total else "—"
    sign = "+" if net_pnl >= 0 else ""

    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Performance Stats*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏆 *All Time*\n"
        f"├ Total Trades: `{total}`\n"
        f"├ Win Rate:     `{wr}`\n"
        f"├ Winners:      `{wins}`\n"
        f"├ Losers:       `{losses}`\n"
        f"└ Net P&L:      `{sign}{net_pnl:.2f}`\n\n"
        "📈 *Bot not yet deployed.*\n"
        "_Stats will populate once auto_\n"
        "_trading begins._"
    )
    keyboard = kb(
        [("📋 Trade History", "td_history"), ("🤖 Auto Trading", "td_auto")],
        [("⬅️ Dashboard",     "td_home")],
    )
    return text, keyboard


# ─── SCREEN 8: Bot Settings ──────────────────────────────────────────────────
def screen_settings(uid: str):
    accts = get_user_accounts(uid)

    def conn(name: str) -> str:
        s = accts.get(name, {}).get("status", "not_set")
        if s == "connected":
            return "🟢 Connected"
        if s == "error":
            return "🔴 Error"
        return "⬜ Not set"

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
        "└ `Paper Trading` _(safe default)_\n\n"
        "🔔 *Notifications*\n"
        "└ `🟢 All alerts ON`\n\n"
        "_To add/edit API keys use_\n"
        "_the main Trading Menu._"
    )
    keyboard = kb(
        [("🔗 Manage APIs", "main_trading_menu"), ("🔔 Alerts", "settings_notif")],
        [("⬅️ Dashboard",   "td_home")],
    )
    return text, keyboard


# ─── Confirm Order ───────────────────────────────────────────────────────────
def screen_confirm(side: str, symbol: str):
    emoji = "🟢" if side == "buy" else "🔴"
    verb = side.upper()
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *Confirm {verb}*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Asset:  `{symbol}`\n"
        f"Side:   `{verb}`\n"
        f"Type:   `Market · Paper`\n"
        f"Risk:   `1% of balance`\n"
        f"SL/TP:  `−2% / +3%`\n\n"
        "Confirm?"
    )
    keyboard = kb(
        [(f"✅ Confirm {verb}", f"confirm_{side}_{symbol}"),
         ("❌ Cancel", "td_manual")],
    )
    return text, keyboard


# ─── Order Placed ────────────────────────────────────────────────────────────
def screen_filled(side: str, symbol: str, uid: str):
    """Records a paper trade and shows confirmation."""
    trades = _load("trades")
    tid = f"TRADE_{uid}_{int(datetime.now(timezone.utc).timestamp())}"
    trades[tid] = {
        "trade_id":    tid,
        "user_id":     int(uid),
        "symbol":      symbol,
        "side":        side.upper(),
        "type":        "MANUAL",
        "order_type":  "MARKET",
        "status":      "OPEN",
        "entry_price": 0,
        "pnl":         0,
        "created_at":  datetime.now(timezone.utc).isoformat(),
    }
    _save("trades", trades)

    emoji = "🟢" if side == "buy" else "🔴"
    text = (
        "✅ *Order Placed!*\n\n"
        f"{emoji} {side.upper()} `{symbol}`\n"
        f"Status: `Filled (Paper)`\n"
        f"Time:   `{ts_now()}`\n\n"
        "Position is now open.\n"
        "You'll be notified on close."
    )
    keyboard = kb(
        [("📋 History", "td_history"), ("🏠 Dashboard", "td_home")],
    )
    return text, keyboard


# ─── /trading COMMAND HANDLER ────────────────────────────────────────────────
async def cmd_trading_dashboard(update, ctx):
    """Handle the /trading command — show trading home."""
    uid = str(update.effective_user.id)
    text, keyboard = screen_trading_home(uid)
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


# ─── CALLBACK ROUTER ─────────────────────────────────────────────────────────
async def handle_trading_callbacks(update, ctx):
    """Route all trading-related callback queries."""
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)

    text, keyboard = None, None

    # Dashboard screens
    if   data == "td_home":     text, keyboard = screen_trading_home(uid)
    elif data == "td_auto":     text, keyboard = screen_auto(uid)
    elif data == "td_manual":   text, keyboard = screen_manual()
    elif data == "td_market":   text, keyboard = screen_market()
    elif data == "td_history":  text, keyboard = screen_history(uid)
    elif data == "td_stats":    text, keyboard = screen_stats(uid)
    elif data == "td_settings": text, keyboard = screen_settings(uid)

    # Pair selection
    elif data.startswith("mt_"):
        symbol = data[3:]
        text, keyboard = screen_trade_detail(symbol)

    # Execute (show confirm)
    elif data.startswith("exec_buy_"):
        text, keyboard = screen_confirm("buy", data[9:])
    elif data.startswith("exec_sell_"):
        text, keyboard = screen_confirm("sell", data[10:])

    # Confirmed order
    elif data.startswith("confirm_buy_"):
        text, keyboard = screen_filled("buy", data[12:], uid)
    elif data.startswith("confirm_sell_"):
        text, keyboard = screen_filled("sell", data[13:], uid)

    # Bot controls
    elif data == "bot_start":
        text = (
            "🤖 *Bot Starting...*\n\n"
            "⚠️ Trading bot is in paper mode.\n"
            "The service is monitoring markets.\n\n"
            "_No real money is at risk._"
        )
        keyboard = kb(
            [("🔧 Configure", "bot_config"), ("⬅️ Back", "td_auto")],
        )
    elif data == "bot_config":
        text = (
            "🔧 *Bot Configuration*\n\n"
            "├ Risk/Trade:  `1%`\n"
            "├ Stop Loss:   `2%`\n"
            "├ Take Profit: `3%`\n"
            "├ Strategy:    `Trend`\n"
            "└ Mode:        `Paper`\n\n"
            "_Edit config on VPS:_\n"
            "`/root/openasset_club/`\n"
            "`trading_bots/config.json`"
        )
        keyboard = kb([("⬅️ Back", "td_auto")])

    elif data == "settings_notif":
        text = "🔔 *Notifications*\n\n✅ All Telegram alerts active."
        keyboard = kb([("⬅️ Settings", "td_settings")])

    if text is None:
        return  # unknown callback — leave for other handlers

    try:
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.warning(f"edit_message_text failed: {e}")
