#!/bin/bash
# OpenAsset — Install Strategy Lab + OANDA + Web Admin + dashboard fixes
set -e
BOT="/root/openasset_club/telegram_bot"
M="$BOT/main.py"
BK="$BOT/main.py.bak.$(date +%Y%m%d_%H%M%S)"

echo "═══════════════════════════════════════════════"
echo "  🏛 OpenAsset — Full Platform Installer"
echo "═══════════════════════════════════════════════"

# 0. Required files in repo?
for f in trading_dashboard.py binance_client.py alpaca_client.py \
         openasset_feeds.py openasset_engine.py oanda_client.py \
         web_api.py web_admin.html web_service.sh; do
    [ -f "$f" ] || { echo "❌ Missing $f — git pull first"; exit 1; }
done
[ -f "$M" ] || { echo "❌ main.py not found"; exit 1; }
echo "✅ All 8 modules present"

# 1. Dependencies
echo ""; echo "🔄 Step 1: Python deps..."
python3 -c "from alpaca.trading.client import TradingClient" 2>/dev/null \
    && echo "✅ alpaca-py present" \
    || { pip install alpaca-py --break-system-packages -q && echo "✅ alpaca-py installed"; }
python3 -c "import yfinance" 2>/dev/null \
    && echo "✅ yfinance present" \
    || { pip install yfinance --break-system-packages -q && echo "✅ yfinance installed"; }
python3 -c "import requests" 2>/dev/null \
    && echo "✅ requests present" \
    || { pip install requests --break-system-packages -q && echo "✅ requests installed"; }
python3 -c "import fastapi, uvicorn" 2>/dev/null \
    && echo "✅ fastapi+uvicorn present" \
    || { pip install fastapi uvicorn --break-system-packages -q && echo "✅ fastapi+uvicorn installed"; }

# 2. Copy modules
echo ""; echo "🔄 Step 2: Copy modules..."
cp trading_dashboard.py binance_client.py alpaca_client.py \
   openasset_feeds.py openasset_engine.py oanda_client.py "$BOT/"
# Web files stay in the repo directory (web_api.py reads from there)
cp web_api.py web_admin.html web_service.sh /root/openasset-trading-bot/ 2>/dev/null || true
echo "✅ Copied 6 bot modules + 3 web files"

# 3. Patch main.py menu buttons (idempotent)
echo ""; echo "🔄 Step 3: Patching main.py menus..."
cp "$M" "$BK"; echo "   📦 Backup: $BK"

python3 << 'PYEOF'
M = "/root/openasset_club/telegram_bot/main.py"
src = open(M).read()
changes = []

# A: Dashboard button in START menu
start_target = 'kbd = [[InlineKeyboardButton("🤖 Trading", callback_data="trading_menu")],'
start_new = ('kbd = [[InlineKeyboardButton("📊 Trading Dashboard", callback_data="td_home")],'
             '[InlineKeyboardButton("🤖 Trading", callback_data="trading_menu")],')
if "📊 Trading Dashboard" in src:
    changes.append("A: start-menu button already present — skip")
elif src.count(start_target) == 1:
    src = src.replace(start_target, start_new)
    changes.append("A: ✅ added Dashboard button to START menu")
else:
    changes.append(f"A: ⚠️ start target found {src.count(start_target)}x — skip")

# B: Dashboard button in platform trading-options screen
opt_target = 'kbd = [[InlineKeyboardButton("⬅️ Back", callback_data="trading_menu")]]'
opt_new = ('kbd = [[InlineKeyboardButton("📊 Open Trading Dashboard", callback_data="td_home")],'
           '[InlineKeyboardButton("⬅️ Back", callback_data="trading_menu")]]')
if "📊 Open Trading Dashboard" in src:
    changes.append("B: options button already present — skip")
elif src.count(opt_target) == 1:
    src = src.replace(opt_target, opt_new)
    changes.append("B: ✅ added Dashboard button to trading-options screen")
else:
    changes.append(f"B: ⚠️ options target found {src.count(opt_target)}x — skip")

open(M, "w").write(src)
for c in changes:
    print("   " + c)
PYEOF

# 4. Syntax check all Python files
echo ""; echo "🔄 Step 4: Syntax check..."
for f in "$M" "$BOT/trading_dashboard.py" "$BOT/binance_client.py" \
         "$BOT/alpaca_client.py" "$BOT/openasset_feeds.py" "$BOT/openasset_engine.py"; do
    if python3 -m py_compile "$f" 2>/tmp/se; then
        echo "✅ $(basename $f)"
    else
        echo "❌ $(basename $f):"; cat /tmp/se
        echo "🔄 Rolling back main.py..."; cp "$BK" "$M"; exit 1
    fi
done

# 5. Quick import sanity
echo ""; echo "🔄 Step 5: Import sanity check..."
cd "$BOT"
python3 -c "
import sys; sys.path.insert(0, '.')
import openasset_feeds, openasset_engine
print('✅ feeds:', len(openasset_feeds.SYMBOL_REGISTRY), 'symbols across', len(openasset_feeds.ASSET_CLASSES), 'classes')
print('✅ engine: monitor thread', 'running' if openasset_engine._monitor_thread and openasset_engine._monitor_thread.is_alive() else 'not running')
" || { echo "❌ import failed"; cp "$BK" "$M"; exit 1; }

# 6. Restart bot
echo ""; echo "🔄 Step 6: Restart bot..."
pkill -f "$BOT/main.py" 2>/dev/null || pkill -f "main.py" 2>/dev/null || true
sleep 2
mkdir -p logs
nohup python3 main.py > logs/user_bot.log 2>&1 &
sleep 3
if ps aux | grep "main.py" | grep -v grep >/dev/null; then
    echo "✅ Bot running (PID $(ps aux | grep 'main.py' | grep -v grep | awk '{print $2}' | head -1))"
else
    echo "❌ Bot did not start:"; tail -20 logs/user_bot.log
    echo "🔄 Rolling back..."; cp "$BK" "$M"
    pkill -f main.py 2>/dev/null || true; sleep 1
    nohup python3 main.py > logs/user_bot.log 2>&1 &
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ DONE — Full Platform Installed"
echo "═══════════════════════════════════════════════"
echo "  Telegram Bot — @openasset_club_bot:"
echo "   • /trading → 🏛 Strategy Lab (40+ assets)"
echo "   • OANDA forex: connect via Trading Menu → OANDA"
echo "   • back_home / Help / Guide Back buttons fixed"
echo ""
echo "  Web Admin Dashboard:"
bash /root/openasset-trading-bot/web_service.sh start 2>/dev/null || true
echo ""
