# 🚨 EMERGENCY: BOT DIAGNOSTIC & RECOVERY GUIDE

Sunny, don't panic! Let's diagnose and fix the bots quickly!

---

## 🔧 STEP 1: CHECK IF VPS IS ALIVE

```bash
ssh root@maxhive.cloud
```

If this connects → VPS is alive ✅

If this FAILS → VPS is down ❌
- Contact Hostinger support
- Check your Hostinger dashboard
- Restart VPS from control panel

---

## 🔧 STEP 2: CHECK IF BOTS ARE RUNNING

```bash
ps aux | grep -E "python|bot" | grep -v grep
```

You should see running processes like:
```
/root/trading_bot/ultimate_bot.py (ATBOT)
/root/btbot/bot.py (BTBOT)
/root/ps1trade/etbot.py (ETBOT)
/root/trading_bots_deployed/bot1_crypto.py (BOT1)
... etc
```

If you see them → Bots are running ✅

If you DON'T see them → Bots crashed ❌
- Go to STEP 3 (Restart Bots)

---

## 🔧 STEP 3: CHECK BOT LOGS FOR ERRORS

### **Check ATBOT (Alpaca) logs:**
```bash
tail -100 /root/trading_bot/ultimate_bot.log
```

Look for:
```
ERROR: 401 Unauthorized
ERROR: Connection refused
ERROR: API key invalid
Exception: ...
```

Common errors:
- **401 Unauthorized** → API key/auth issue
- **Connection refused** → Can't reach API
- **Module not found** → Missing dependency

---

### **Check BTBOT logs:**
```bash
tail -100 /root/btbot/bot.log
```

---

### **Check ETBOT logs:**
```bash
tail -100 /root/ps1trade/etbot.log
```

---

### **Check Bot1-5 logs:**
```bash
tail -100 /root/trading_bots_deployed/bot1_crypto.log
tail -100 /root/trading_bots_deployed/bot2_stock.log
tail -100 /root/trading_bots_deployed/bot3_commodity.log
tail -100 /root/trading_bots_deployed/bot4_forex.log
tail -100 /root/trading_bots_deployed/bot5_scalper.log
```

---

## 🔧 STEP 4: RESTART ALL BOTS

### **Kill all running bot processes:**
```bash
pkill -f "python.*bot"
pkill -f "ultimate_bot"
pkill -f "btbot"
pkill -f "etbot"
```

Verify all killed:
```bash
ps aux | grep -E "bot|python" | grep -v grep
```

Should show nothing (or just grep process) ✅

---

### **Restart ATBOT:**
```bash
cd /root/trading_bot
nohup python3 ultimate_bot.py > ultimate_bot.log 2>&1 &
```

---

### **Restart BTBOT:**
```bash
cd /root/btbot
nohup python3 bot.py > bot.log 2>&1 &
```

---

### **Restart ETBOT:**
```bash
cd /root/ps1trade
nohup python3 etbot.py > etbot.log 2>&1 &
```

---

### **Restart Bot1-5:**
```bash
cd /root/trading_bots_deployed

nohup python3 bot1_crypto.py > bot1_crypto.log 2>&1 &
nohup python3 bot2_stock.py > bot2_stock.log 2>&1 &
nohup python3 bot3_commodity.py > bot3_commodity.log 2>&1 &
nohup python3 bot4_forex.py > bot4_forex.log 2>&1 &
nohup python3 bot5_scalper.py > bot5_scalper.log 2>&1 &
```

---

### **Restart Payment Bot (if used):**
```bash
cd /root
nohup python3 telegram_bot_crypto_payments.py > bot_payment.log 2>&1 &
```

---

### **Restart Dashboard:**
```bash
cd /root
python3 -m http.server 8000 &
```

---

## ✅ STEP 5: VERIFY ALL BOTS RESTARTED

```bash
ps aux | grep -E "bot|http.server" | grep -v grep
```

Should show:
```
root  12345  0.0  0.5  ultimate_bot.py
root  12346  0.0  0.5  bot.py (btbot)
root  12347  0.0  0.5  etbot.py
root  12348  0.0  0.5  bot1_crypto.py
root  12349  0.0  0.5  bot2_stock.py
root  12350  0.0  0.5  bot3_commodity.py
root  12351  0.0  0.5  bot4_forex.py
root  12352  0.0  0.5  bot5_scalper.py
root  12353  0.0  0.5  telegram_bot_crypto_payments.py
root  12354  0.0  0.5  http.server
```

If you see these → All bots restarted! ✅

---

## 🔧 STEP 6: CHECK VPS HEALTH

```bash
# Check CPU usage
top -b -n 1 | head -20

# Check memory
free -h

# Check disk space
df -h /root

# Check network
ping google.com -c 1
```

If all look good → No system issues ✅

If not:
- **High CPU** → Kill heavy processes
- **No memory** → Restart VPS
- **No disk space** → Delete old logs
- **No network** → Contact Hostinger

---

## 🔧 STEP 7: TEST TELEGRAM BOTS

### **Test Payment Bot:**
```bash
# Send /start to @openasset_club_bot in Telegram

# Expected: Main menu appears
```

### **Test Telegram Alerts:**
```bash
# Check if your Telegram chat receives messages
# Should get alerts from bots

# Check your Chat ID: 5587885687
```

---

## 🔧 COMMON ISSUES & FIXES

### **Issue: All bots stopped at same time**

**Cause 1: VPS restarted**
```bash
# Solution: Restart all bots (see STEP 4)
```

**Cause 2: Out of memory**
```bash
# Check memory:
free -h

# Solution: Restart VPS
sudo reboot

# Then restart all bots
```

**Cause 3: Out of disk space**
```bash
# Check disk:
df -h /root

# Solution: Delete old logs
rm -f /root/*/*.log
rm -f /root/*.log

# Then restart bots
```

**Cause 4: Bot process crashed**
```bash
# Check logs:
tail -50 /root/trading_bot/ultimate_bot.log

# Look for ERROR or Exception

# Solution: Fix error or restart bot
```

---

### **Issue: ATBOT shows 401 Authorization Error**

```bash
# This has been a recurring issue

# Solution 1: Try again (temporary fix)
pkill -f ultimate_bot
cd /root/trading_bot
nohup python3 ultimate_bot.py > ultimate_bot.log 2>&1 &

# Solution 2: Contact Alpaca support
# Account: 261356293
# Issue: Host not in allowlist (403/401 errors)
# Tell them: "IP 72.62.254.237 needs allowlist clearance"

# Solution 3: Update API credentials
nano /root/.env_ALPACA
# Update ALPACA_API_KEY and ALPACA_SECRET_KEY
# Save and restart bot
```

---

### **Issue: BTBOT can't connect to Binance**

```bash
# Check network:
ping api.binance.com -c 1

# Should show response

# If no response:
# - VPS network issue
# - Contact Hostinger

# If yes:
# - Check Binance API key
nano /root/.env_BINANCE
# Verify API_KEY and SECRET_KEY are correct
```

---

### **Issue: Missing Python packages**

```bash
# Check what's missing:
pip list | grep -E "binance|alpaca|telegram"

# Install missing:
pip install python-binance alpaca-trade-api python-telegram-bot

# Then restart bots
```

---

## 📊 STEP 8: CREATE MONITORING SCRIPT

Create auto-restart script:

```bash
cat > /root/monitor_bots.sh << 'EOF'
#!/bin/bash

# Auto-restart bots every hour if they crash

while true; do
    # Check each bot
    if ! pgrep -f "ultimate_bot" > /dev/null; then
        echo "ATBOT crashed! Restarting..."
        cd /root/trading_bot
        nohup python3 ultimate_bot.py > ultimate_bot.log 2>&1 &
    fi

    if ! pgrep -f "btbot/bot.py" > /dev/null; then
        echo "BTBOT crashed! Restarting..."
        cd /root/btbot
        nohup python3 bot.py > bot.log 2>&1 &
    fi

    if ! pgrep -f "etbot" > /dev/null; then
        echo "ETBOT crashed! Restarting..."
        cd /root/ps1trade
        nohup python3 etbot.py > etbot.log 2>&1 &
    fi

    if ! pgrep -f "bot1_crypto" > /dev/null; then
        echo "BOT1 crashed! Restarting..."
        cd /root/trading_bots_deployed
        nohup python3 bot1_crypto.py > bot1_crypto.log 2>&1 &
    fi

    if ! pgrep -f "bot2_stock" > /dev/null; then
        echo "BOT2 crashed! Restarting..."
        cd /root/trading_bots_deployed
        nohup python3 bot2_stock.py > bot2_stock.log 2>&1 &
    fi

    if ! pgrep -f "bot3_commodity" > /dev/null; then
        echo "BOT3 crashed! Restarting..."
        cd /root/trading_bots_deployed
        nohup python3 bot3_commodity.py > bot3_commodity.log 2>&1 &
    fi

    if ! pgrep -f "bot4_forex" > /dev/null; then
        echo "BOT4 crashed! Restarting..."
        cd /root/trading_bots_deployed
        nohup python3 bot4_forex.py > bot4_forex.log 2>&1 &
    fi

    if ! pgrep -f "bot5_scalper" > /dev/null; then
        echo "BOT5 crashed! Restarting..."
        cd /root/trading_bots_deployed
        nohup python3 bot5_scalper.py > bot5_scalper.log 2>&1 &
    fi

    # Check every 5 minutes
    sleep 300
done
EOF

chmod +x /root/monitor_bots.sh

# Start monitoring in background
nohup /root/monitor_bots.sh > /root/monitor_bots.log 2>&1 &
```

Now bots auto-restart if they crash! ✅

---

## 📋 QUICK RECOVERY CHECKLIST

```
☐ Step 1: SSH to VPS (verify VPS alive)
☐ Step 2: Check if bots running (ps aux)
☐ Step 3: Check logs for errors (tail -100 logs)
☐ Step 4: Kill all bots (pkill)
☐ Step 5: Restart all bots (nohup commands)
☐ Step 6: Verify all running (ps aux)
☐ Step 7: Check system health (free, df, top)
☐ Step 8: Test in Telegram
☐ Step 9: Set up monitoring script
☐ Step 10: Monitor for 30 minutes (make sure no crashes)

Result: All bots running again! ✅
```

---

## 🎯 IF BOTS STILL NOT WORKING

Send me:
```
1. Output of: ps aux | grep bot
2. Output of: tail -50 /root/trading_bot/ultimate_bot.log
3. Output of: free -h
4. Output of: df -h /root
5. Output of: ping google.com -c 1
```

And I'll help you fix it! 💪

---

## 🚀 PERMANENT FIX: CRON JOB

Add to crontab to auto-restart bots daily:

```bash
crontab -e

# Add these lines:
@reboot /root/monitor_bots.sh
0 0 * * * /root/restart_bots.sh
```

This ensures:
- ✅ Bots restart on VPS reboot
- ✅ Bots restart daily at midnight
- ✅ Monitoring script auto-starts

---

**Run the diagnostic steps above now!** 🚀

Tell me what you find and I'll help fix it! 💪
