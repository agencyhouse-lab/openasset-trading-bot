#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  OpenAsset Trading Dashboard — Safe Installer
#  Run from: /root/openasset-trading-bot
#  Usage:    bash install_trading_dashboard.sh
# ═══════════════════════════════════════════════════════════════════════════

set -e  # exit on any error

BOT_DIR="/root/openasset_club/telegram_bot"
MAIN_PY="$BOT_DIR/main.py"
BACKUP_PY="$BOT_DIR/main.py.bak.$(date +%Y%m%d_%H%M%S)"
SRC_FILE="trading_dashboard.py"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 OpenAsset Trading Dashboard Installer"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── 1. Verify we're in the right place ──────────────────────────────────────
if [ ! -f "$SRC_FILE" ]; then
    echo "❌ ERROR: $SRC_FILE not found in current directory"
    echo "   Run from: /root/openasset-trading-bot"
    echo "   Try: cd /root/openasset-trading-bot && git pull"
    exit 1
fi

if [ ! -f "$MAIN_PY" ]; then
    echo "❌ ERROR: main.py not found at $MAIN_PY"
    exit 1
fi

echo "✅ Source files found"

# ─── 2. Kill duplicate trading_bot_service ──────────────────────────────────
echo ""
echo "🔄 Step 1: Cleaning up duplicate processes..."
DUPES=$(ps aux | grep trading_bot_service | grep -v grep | awk '{print $2}')
COUNT=$(echo "$DUPES" | grep -c . || echo 0)

if [ "$COUNT" -gt 1 ]; then
    # Keep the newest (last) PID, kill the rest
    OLDEST=$(echo "$DUPES" | head -n -1)
    echo "   Found $COUNT instances, keeping newest, killing: $OLDEST"
    for pid in $OLDEST; do
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
    echo "✅ Cleaned up duplicates"
else
    echo "✅ No duplicates ($COUNT instance running)"
fi

# ─── 3. Copy trading_dashboard.py ────────────────────────────────────────────
echo ""
echo "🔄 Step 2: Installing trading_dashboard.py..."
cp "$SRC_FILE" "$BOT_DIR/"
echo "✅ Copied to $BOT_DIR/"

# ─── 4. Patch main.py (using Python — safe + reversible) ────────────────────
echo ""
echo "🔄 Step 3: Patching main.py..."

# Backup first
cp "$MAIN_PY" "$BACKUP_PY"
echo "   📦 Backup: $BACKUP_PY"

# Use Python for safe AST-aware patching
python3 << 'PYEOF'
import re
import sys

MAIN = "/root/openasset_club/telegram_bot/main.py"

with open(MAIN) as f:
    src = f.read()

IMPORT_LINE = (
    "from trading_dashboard import "
    "cmd_trading_dashboard, handle_trading_callbacks, TRADING_CALLBACK_PATTERN"
)
HANDLER_CMD = (
    'app.add_handler(CommandHandler("trading", cmd_trading_dashboard))'
)
HANDLER_CB = (
    "app.add_handler(CallbackQueryHandler("
    "handle_trading_callbacks, pattern=TRADING_CALLBACK_PATTERN))"
)

# Idempotency: skip if already patched
if "trading_dashboard" in src:
    print("   ✅ main.py already patched — skipping")
    sys.exit(0)

# ── 1. Inject import after the last `from telegram` line ──
lines = src.split("\n")
last_telegram = -1
for i, line in enumerate(lines):
    if line.startswith("from telegram") or line.startswith("import telegram"):
        last_telegram = i

if last_telegram == -1:
    print("   ❌ Could not find telegram imports — aborting")
    sys.exit(1)

lines.insert(last_telegram + 1, IMPORT_LINE)
patched = "\n".join(lines)

# ── 2. Inject handler registration ──
# Try to find an existing add_handler line and inject ours nearby
handler_pat = re.compile(
    r"^(\s*)(app|application)\.add_handler\(",
    re.MULTILINE,
)
match = handler_pat.search(patched)

if match:
    indent = match.group(1)
    var = match.group(2)
    injection = (
        f"\n{indent}# --- Trading Dashboard (auto-injected) ---\n"
        f"{indent}{var}.add_handler(CommandHandler(\"trading\", cmd_trading_dashboard))\n"
        f"{indent}{var}.add_handler(CallbackQueryHandler("
        f"handle_trading_callbacks, pattern=TRADING_CALLBACK_PATTERN))\n"
    )
    patched = patched[:match.start()] + injection + patched[match.start():]
    print("   ✅ Injected handler registration before existing handlers")
else:
    # Fallback: try inserting before run_polling
    rp_pat = re.compile(r"^(\s*)(app|application)\.run_polling\(", re.MULTILINE)
    rp = rp_pat.search(patched)
    if rp:
        indent = rp.group(1)
        var = rp.group(2)
        injection = (
            f"{indent}# --- Trading Dashboard (auto-injected) ---\n"
            f"{indent}{var}.add_handler(CommandHandler(\"trading\", cmd_trading_dashboard))\n"
            f"{indent}{var}.add_handler(CallbackQueryHandler("
            f"handle_trading_callbacks, pattern=TRADING_CALLBACK_PATTERN))\n"
        )
        patched = patched[:rp.start()] + injection + patched[rp.start():]
        print("   ✅ Injected handler registration before run_polling()")
    else:
        print("   ⚠️  Could not auto-inject handlers")
        print("       You'll need to manually add these lines in main():")
        print("       " + HANDLER_CMD)
        print("       " + HANDLER_CB)

with open(MAIN, "w") as f:
    f.write(patched)

print("   ✅ main.py patched successfully")
PYEOF

# ─── 5. Syntax-check the patched file ────────────────────────────────────────
echo ""
echo "🔄 Step 4: Syntax-checking patched main.py..."
if python3 -m py_compile "$MAIN_PY" 2>/tmp/syntax_err; then
    echo "✅ main.py syntax OK"
else
    echo "❌ SYNTAX ERROR in patched main.py!"
    cat /tmp/syntax_err
    echo ""
    echo "🔄 Rolling back to backup..."
    cp "$BACKUP_PY" "$MAIN_PY"
    echo "✅ Restored. No changes applied."
    exit 1
fi

# ─── 6. Restart the user bot ─────────────────────────────────────────────────
echo ""
echo "🔄 Step 5: Restarting user bot..."
pkill -f "$BOT_DIR/main.py" 2>/dev/null || pkill -f "main.py" 2>/dev/null || true
sleep 2

cd "$BOT_DIR"
mkdir -p logs
nohup python3 main.py > logs/user_bot.log 2>&1 &
sleep 3

# ─── 7. Verify ───────────────────────────────────────────────────────────────
echo ""
echo "🔄 Step 6: Verifying..."
if ps aux | grep "main.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}' | head -1)
    echo "✅ User bot running (PID: $PID)"
else
    echo "❌ User bot did NOT start! Check logs:"
    tail -20 "$BOT_DIR/logs/user_bot.log"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ TRADING DASHBOARD INSTALLED!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  📱 Test in Telegram:"
echo "     1. Open @openasset_club_bot"
echo "     2. Send:  /trading"
echo "     3. Click through the 8 screens"
echo ""
echo "  📋 If anything breaks:"
echo "     cp $BACKUP_PY $MAIN_PY"
echo "     pkill -f main.py && cd $BOT_DIR && nohup python3 main.py > logs/user_bot.log 2>&1 &"
echo ""
echo "  📝 View logs:"
echo "     tail -f $BOT_DIR/logs/user_bot.log"
echo ""
