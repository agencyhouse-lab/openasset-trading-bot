#!/bin/bash
# OpenAsset — Diagnostic + Junk Cleanup (read-only on main.py)
BOT="/root/openasset_club/telegram_bot"
M="$BOT/main.py"

echo "════════════ DIAGNOSTIC REPORT ════════════"

echo ""
echo "── 1. Cleaning junk files (paste accidents) ──"
# Files with spaces in the name are paste-accidents; Python can't import them
find "$BOT" -maxdepth 1 -name "* *" -type f -print -delete 2>/dev/null || true
echo "   done"

echo ""
echo "── 2. Python files present ──"
ls -1 "$BOT"/*.py 2>/dev/null

echo ""
echo "── 3. live_mode + connection status ──"
python3 -c "
import json
d = json.load(open('$BOT/database/accounts.json'))
for u, a in d.items():
    bn = a.get('binance', {})
    al = a.get('alpaca', {})
    print(f'  User {u}:')
    print(f'    binance: status={bn.get(\"status\")} live_mode={bn.get(\"live_mode\")}')
    print(f'    alpaca:  status={al.get(\"status\")}')
"

echo ""
echo "── 4. Module import test ──"
cd "$BOT"
python3 -c "import trading_dashboard; print('  ✅ trading_dashboard imports OK')" 2>&1 | head -15
python3 -c "import binance_client; print('  ✅ binance_client imports OK')" 2>&1 | head -15

echo ""
echo "── 5. CommandHandlers + async defs ──"
grep -nE "CommandHandler\(|^async def|^    async def" "$M" | head -40

echo ""
echo "── 6. Handler registration (order matters!) ──"
grep -nE "add_handler|CallbackQueryHandler|run_polling" "$M"

echo ""
echo "── 7. ALL callback_data names in main.py ──"
grep -noE "callback_data=['\"][^'\"]+['\"]" "$M" | sed "s/callback_data=//" | sort -u

echo ""
echo "── 8. Home/menu/trading/alpaca references ──"
grep -nE "main_menu|main_trading_menu|trading_menu|'trading'|\"trading\"|def.*menu|home" "$M" | head -30

echo ""
echo "── 9. Alpaca references ──"
grep -niE "alpaca" "$M" | head -25

echo ""
echo "════════════ END REPORT ════════════"
echo "Copy everything above and send it back."
