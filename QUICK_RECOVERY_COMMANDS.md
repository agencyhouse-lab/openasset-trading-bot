# ⚡ QUICK RECOVERY - RUN THESE COMMANDS NOW!

Sunny, run these commands one by one to bring all bots back online!

---

## 🚀 STEP 1: SSH INTO VPS

```bash
ssh root@maxhive.cloud
```

---

## 🚀 STEP 2: KILL ALL CRASHED BOTS

```bash
pkill -f "python.*bot"
pkill -f ultimate_bot
pkill -f btbot
pkill -f etbot
```

Wait 2 seconds...

---

## 🚀 STEP 3: RESTART ATBOT (Alpaca)

```bash
cd /root/trading_bot
nohup python3 ultimate_bot.py > ultimate_bot.log 2>&1 &
```

---

## 🚀 STEP 4: RESTART BTBOT (Binance)

```bash
cd /root/btbot
nohup python3 bot.py > bot.log 2>&1 &
```

---

## 🚀 STEP 5: RESTART ETBOT (eToro)

```bash
cd /root/ps1trade
nohup python3 etbot.py > etbot.log 2>&1 &
```

---

## 🚀 STEP 6: RESTART BOT1-BOT5

```bash
cd /root/trading_bots_deployed

nohup python3 bot1_crypto.py > bot1_crypto.log 2>&1 &
nohup python3 bot2_stock.py > bot2_stock.log 2>&1 &
nohup python3 bot3_commodity.py > bot3_commodity.log 2>&1 &
nohup python3 bot4_forex.py > bot4_forex.log 2>&1 &
nohup python3 bot5_scalper.py > bot5_scalper.log 2>&1 &
```

---

## 🚀 STEP 7: RESTART PAYMENT BOT

```bash
cd /root
nohup python3 telegram_bot_crypto_payments.py > bot_payment.log 2>&1 &
```

---

## 🚀 STEP 8: RESTART DASHBOARD

```bash
cd /root
python3 -m http.server 8000 &
```

---

## ✅ STEP 9: VERIFY ALL RUNNING

```bash
ps aux | grep -E "bot|http.server" | grep -v grep
```

You should see:
- ✅ ultimate_bot.py (ATBOT)
- ✅ btbot/bot.py (BTBOT)
- ✅ etbot.py (ETBOT)
- ✅ bot1_crypto.py (BOT1)
- ✅ bot2_stock.py (BOT2)
- ✅ bot3_commodity.py (BOT3)
- ✅ bot4_forex.py (BOT4)
- ✅ bot5_scalper.py (BOT5)
- ✅ telegram_bot_crypto_payments.py (Payment)
- ✅ http.server 8000 (Dashboard)

If you see all 10 → SUCCESS! ✅

---

## 🔍 STEP 10: CHECK FOR ERRORS

```bash
# Check logs for errors
echo "=== ATBOT LOG ===" && tail -20 /root/trading_bot/ultimate_bot.log && \
echo "" && \
echo "=== BTBOT LOG ===" && tail -20 /root/btbot/bot.log && \
echo "" && \
echo "=== ETBOT LOG ===" && tail -20 /root/ps1trade/etbot.log && \
echo "" && \
echo "=== BOT1 LOG ===" && tail -20 /root/trading_bots_deployed/bot1_crypto.log
```

If you see errors, check: **BOT_EMERGENCY_RECOVERY.md** for fixes

---

## 📱 STEP 11: TEST TELEGRAM

Send to Telegram Chat (ID: 5587885687) or your trading group:

```
/start

Should see: All bots responding ✅
Should see: Telegram alerts coming in ✅
```

---

## 💾 STEP 12: SET UP AUTO-RESTART (OPTIONAL BUT RECOMMENDED)

Make sure bots auto-restart if they crash again:

```bash
cat > /root/restart_bots.sh << 'EOF'
#!/bin/bash
pkill -f "python.*bot"
sleep 1
cd /root/trading_bot && nohup python3 ultimate_bot.py > ultimate_bot.log 2>&1 &
cd /root/btbot && nohup python3 bot.py > bot.log 2>&1 &
cd /root/ps1trade && nohup python3 etbot.py > etbot.log 2>&1 &
cd /root/trading_bots_deployed && nohup python3 bot1_crypto.py > bot1_crypto.log 2>&1 &
cd /root/trading_bots_deployed && nohup python3 bot2_stock.py > bot2_stock.log 2>&1 &
cd /root/trading_bots_deployed && nohup python3 bot3_commodity.py > bot3_commodity.log 2>&1 &
cd /root/trading_bots_deployed && nohup python3 bot4_forex.py > bot4_forex.log 2>&1 &
cd /root/trading_bots_deployed && nohup python3 bot5_scalper.py > bot5_scalper.log 2>&1 &
cd /root && nohup python3 telegram_bot_crypto_payments.py > bot_payment.log 2>&1 &
cd /root && python3 -m http.server 8000 &
EOF

chmod +x /root/restart_bots.sh

# Test the script
/root/restart_bots.sh

# Add to crontab to auto-run daily at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /root/restart_bots.sh") | crontab -
```

Now bots auto-restart daily! ✅

---

## 🎯 IF BOTS STILL NOT WORKING

1. Open file: **BOT_EMERGENCY_RECOVERY.md**
2. Follow the diagnostic steps
3. Check logs for specific errors
4. Send me the error messages

---

## ✨ YOUR 12-STEP CHECKLIST

```
☐ 1. SSH to VPS
☐ 2. Kill all bots
☐ 3. Restart ATBOT
☐ 4. Restart BTBOT
☐ 5. Restart ETBOT
☐ 6. Restart BOT1-5
☐ 7. Restart Payment Bot
☐ 8. Restart Dashboard
☐ 9. Verify all running
☐ 10. Check logs
☐ 11. Test Telegram
☐ 12. Set up auto-restart

Total time: ~5 minutes
Result: All bots back online! ✅
```

---

## 🚀 RUN NOW!

Copy and paste each command into terminal in order.

**Don't wait!** Start with Step 1: SSH to VPS

All bots will be back online in 5 minutes! 💪

---

When done, send me:
```
✅ All bots restarted
✅ All showing in ps aux
✅ Telegram alerts working
✅ Dashboard loading
```

Then we'll fix any remaining issues! 💎
