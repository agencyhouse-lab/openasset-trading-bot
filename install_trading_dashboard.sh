#!/bin/bash
# OpenAsset — Install Strategy Lab + Alpaca + dashboard fixes
set -e
BOT="/root/openasset_club/telegram_bot"
M="$BOT/main.py"
BK="$BOT/main.py.bak.$(date +%Y%m%d_%H%M%S)"

echo "═══════════════════════════════════════════════"
echo "  🏛 OpenAsset — Strategy Lab Installer"
echo "═══════════════════════════════════════════════"

# 0. Required files in repo?
for f in trading_dashboard.py binance_client.py alpaca_client.py \
         openasset_feeds.py openasset_engine.py; do
    [ -f "$f" ] || { echo "❌ Missing $f — git pull first"; exit 1; }
done
[ -f "$M" ] || { echo "❌ main.py not found"; exit 1; }
echo "✅ All 5 modules present"

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

# 2. Copy modules
echo ""; echo "🔄 Step 2: Copy modules..."
cp trading_dashboard.py binance_client.py alpaca_client.py \
   openasset_feeds.py openasset_engine.py "$BOT/"
echo "✅ Copied 5 modules"

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
echo "  ✅ DONE — Strategy Lab is live"
echo "═══════════════════════════════════════════════"
echo "  Test in @openasset_club_bot:"
echo "   • /trading → tap 🏛 Strategy Lab"
echo "   • Pick Crypto → BTC → BUY \$50 → auto SL/TP set"
echo "   • Help / FAQ / Guide → Back buttons now work"
echo ""
