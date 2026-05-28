#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  OpenAsset Trading Dashboard — Safe Installer (with Binance Live)
#  Run from: /root/openasset-trading-bot
#  Usage:    bash install_trading_dashboard.sh
# ═══════════════════════════════════════════════════════════════════════════

set -e

BOT_DIR="/root/openasset_club/telegram_bot"
MAIN_PY="$BOT_DIR/main.py"
BACKUP_PY="$BOT_DIR/main.py.bak.$(date +%Y%m%d_%H%M%S)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 OpenAsset Trading Dashboard Installer (Binance Live)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── 1. Sanity checks ────────────────────────────────────────────────────────
for f in trading_dashboard.py binance_client.py; do
    if [ ! -f "$f" ]; then
        echo "❌ ERROR: $f not found. Run: git pull origin main"
        exit 1
    fi
done

if [ ! -f "$MAIN_PY" ]; then
    echo "❌ ERROR: main.py not found at $MAIN_PY"
    exit 1
fi

echo "✅ Source files found"

# ─── 2. Verify python-binance installed ──────────────────────────────────────
echo ""
echo "🔄 Step 1: Checking python-binance..."
if python3 -c "from binance.client import Client" 2>/dev/null; then
    echo "✅ python-binance installed"
else
    echo "📦 Installing python-binance..."
    pip install python-binance --break-system-packages
fi

# ─── 3. Kill duplicate trading_bot_service ───────────────────────────────────
echo ""
echo "🔄 Step 2: Cleaning up duplicate processes..."
DUPES=$(ps aux | grep trading_bot_service | grep -v grep | awk '{print $2}')
COUNT=$(echo "$DUPES" | grep -c . 2>/dev/null || echo 0)
if [ "$COUNT" -gt 1 ]; then
    OLDEST=$(echo "$DUPES" | head -n -1)
    echo "   Found $COUNT instances, killing old PIDs: $OLDEST"
    for pid in $OLDEST; do
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
fi
echo "✅ Process cleanup done"

# ─── 4. Copy module files ────────────────────────────────────────────────────
echo ""
echo "🔄 Step 3: Installing modules..."
cp trading_dashboard.py "$BOT_DIR/"
cp binance_client.py    "$BOT_DIR/"
echo "✅ Copied to $BOT_DIR/"

# ─── 5. Patch main.py (idempotent) ───────────────────────────────────────────
echo ""
echo "🔄 Step 4: Checking main.py for trading handlers..."

if grep -q "trading_dashboard" "$MAIN_PY"; then
    echo "✅ main.py already has trading dashboard wired in — skipping patch"
else
    cp "$MAIN_PY" "$BACKUP_PY"
    echo "   📦 Backup: $BACKUP_PY"

    python3 << 'PYEOF'
import re, sys
MAIN = "/root/openasset_club/telegram_bot/main.py"
with open(MAIN) as f:
    src = f.read()

IMPORT_LINE = (
    "from trading_dashboard import "
    "cmd_trading_dashboard, handle_trading_callbacks, TRADING_CALLBACK_PATTERN"
)

lines = src.split("\n")
last_telegram = -1
for i, line in enumerate(lines):
    if line.startswith("from telegram") or line.startswith("import telegram"):
        last_telegram = i
if last_telegram == -1:
    print("   ❌ Could not find telegram imports")
    sys.exit(1)

lines.insert(last_telegram + 1, IMPORT_LINE)
patched = "\n".join(lines)

handler_pat = re.compile(r"^(\s*)(app|application)\.add_handler\(", re.MULTILINE)
m = handler_pat.search(patched)
if m:
    indent, var = m.group(1), m.group(2)
    injection = (
        f"\n{indent}# --- Trading Dashboard (auto-injected) ---\n"
        f"{indent}{var}.add_handler(CommandHandler(\"trading\", cmd_trading_dashboard))\n"
        f"{indent}{var}.add_handler(CallbackQueryHandler("
        f"handle_trading_callbacks, pattern=TRADING_CALLBACK_PATTERN))\n"
    )
    patched = patched[:m.start()] + injection + patched[m.start():]
    print("   ✅ Injected /trading + callback handler")
else:
    print("   ⚠️  Could not auto-inject handlers — add manually")

with open(MAIN, "w") as f:
    f.write(patched)
print("   ✅ main.py patched")
PYEOF
fi

# ─── 6. Syntax check ─────────────────────────────────────────────────────────
echo ""
echo "🔄 Step 5: Syntax-checking files..."
for f in "$MAIN_PY" "$BOT_DIR/trading_dashboard.py" "$BOT_DIR/binance_client.py"; do
    if python3 -m py_compile "$f" 2>/tmp/syntax_err; then
        echo "✅ $(basename $f) OK"
    else
        echo "❌ SYNTAX ERROR in $(basename $f):"
        cat /tmp/syntax_err
        if [ -f "$BACKUP_PY" ]; then
            echo "🔄 Rolling back main.py..."
            cp "$BACKUP_PY" "$MAIN_PY"
        fi
        exit 1
    fi
done

# ─── 7. Restart user bot ─────────────────────────────────────────────────────
echo ""
echo "🔄 Step 6: Restarting user bot..."
pkill -f "$BOT_DIR/main.py" 2>/dev/null || pkill -f "main.py" 2>/dev/null || true
sleep 2
cd "$BOT_DIR"
mkdir -p logs
nohup python3 main.py > logs/user_bot.log 2>&1 &
sleep 3

if ps aux | grep "main.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}' | head -1)
    echo "✅ User bot running (PID: $PID)"
else
    echo "❌ User bot did NOT start! Logs:"
    tail -20 "$BOT_DIR/logs/user_bot.log"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ LIVE TRADING INSTALLED!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  📱 Test in Telegram (@openasset_club_bot):"
echo "     1. /trading                  → shows real USDT balance"
echo "     2. ⚙️ Bot Settings           → ✅ Verify Binance"
echo "     3. ⚙️ Bot Settings           → 🔴 Enable LIVE MODE"
echo "     4. ✏️ Manual → BTC/USD       → place a small BUY"
echo ""
echo "  📝 Logs:  tail -f $BOT_DIR/logs/user_bot.log"
echo ""
