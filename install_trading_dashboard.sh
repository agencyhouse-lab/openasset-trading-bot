#!/bin/bash
# OpenAsset — Install Alpaca + fix home button + link /trading into menus
set -e
BOT="/root/openasset_club/telegram_bot"
M="$BOT/main.py"
BK="$BOT/main.py.bak.$(date +%Y%m%d_%H%M%S)"

echo "═══════════════════════════════════════════════"
echo "  📊 OpenAsset — Alpaca + Menu Fixes Installer"
echo "═══════════════════════════════════════════════"

for f in trading_dashboard.py binance_client.py alpaca_client.py; do
    [ -f "$f" ] || { echo "❌ Missing $f — run: git pull origin main"; exit 1; }
done
[ -f "$M" ] || { echo "❌ main.py not found"; exit 1; }
echo "✅ Source files present"

# 1. Install alpaca-py
echo ""; echo "🔄 Step 1: alpaca-py..."
if python3 -c "from alpaca.trading.client import TradingClient" 2>/dev/null; then
    echo "✅ alpaca-py already installed"
else
    pip install alpaca-py --break-system-packages -q && echo "✅ alpaca-py installed"
fi

# 2. Copy modules
echo ""; echo "🔄 Step 2: Copying modules..."
cp trading_dashboard.py binance_client.py alpaca_client.py "$BOT/"
echo "✅ Copied 3 modules"

# 3. Patch main.py menus
echo ""; echo "🔄 Step 3: Patching main.py menus..."
cp "$M" "$BK"; echo "   📦 Backup: $BK"

python3 << 'PYEOF'
M = "/root/openasset_club/telegram_bot/main.py"
src = open(M).read()
changes = []

# --- Patch A: add Dashboard button to START menu ---
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

# --- Patch B: add Dashboard button to platform trading-options screen ---
opt_target = 'kbd = [[InlineKeyboardButton("⬅️ Back", callback_data="trading_menu")]]'
opt_new = ('kbd = [[InlineKeyboardButton("📊 Open Trading Dashboard", callback_data="td_home")],'
           '[InlineKeyboardButton("⬅️ Back", callback_data="trading_menu")]]')
if "📊 Open Trading Dashboard" in src:
    changes.append("B: options button already present — skip")
elif src.count(opt_target) == 1:
    src = src.replace(opt_target, opt_new)
    changes.append("B: ✅ added Dashboard button to trading-options screen")
else:
    changes.append(f"B: ⚠️ options target found {src.count(opt_target)}x — skip (will link via START menu instead)")

open(M, "w").write(src)
for c in changes:
    print("   " + c)
PYEOF

# 4. Syntax check all
echo ""; echo "🔄 Step 4: Syntax check..."
for f in "$M" "$BOT/trading_dashboard.py" "$BOT/binance_client.py" "$BOT/alpaca_client.py"; do
    if python3 -m py_compile "$f" 2>/tmp/se; then
        echo "✅ $(basename $f)"
    else
        echo "❌ $(basename $f):"; cat /tmp/se
        echo "🔄 Rolling back main.py..."; cp "$BK" "$M"; exit 1
    fi
done

# 5. Restart
echo ""; echo "🔄 Step 5: Restart bot..."
pkill -f "$BOT/main.py" 2>/dev/null || pkill -f "main.py" 2>/dev/null || true
sleep 2
cd "$BOT"; mkdir -p logs
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
echo "  ✅ DONE — Alpaca + fixes installed"
echo "═══════════════════════════════════════════════"
echo "  Test in @openasset_club_bot:"
echo "   • /start → '📊 Trading Dashboard' button now there"
echo "   • /trading → 🏠 Main Menu button now works"
echo "   • Manual → SPY → BUY → real Alpaca paper order"
echo ""
