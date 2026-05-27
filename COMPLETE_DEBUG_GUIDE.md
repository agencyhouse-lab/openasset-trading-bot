# 🔧 COMPLETE DEBUGGING GUIDE

## THE ISSUE
Bot shows as running but doesn't respond to commands.

This means the bot **starts but then crashes**, usually due to:
1. ❌ Invalid bot token
2. ❌ Missing Python packages
3. ❌ Error in bot code (import errors, syntax errors)
4. ❌ .env file not loaded properly

---

## 🎯 STEP-BY-STEP FIX

### **STEP 1: Get the Bot Logs**

Run this command:
```bash
ssh root@maxhive.cloud "tail -100 /root/openasset_club/telegram_bot/logs/bot.log"
```

**Copy the entire output and send it to me!**

The logs will show EXACTLY what's wrong.

---

### **STEP 2: Replace with SIMPLER Bot**

I created a simpler version with better error handling.

**Download:** `main_SIMPLE.py` from outputs folder

**Upload it:**
```bash
scp main_SIMPLE.py root@maxhive.cloud:/root/openasset_club/telegram_bot/main.py
```

**Restart bot:**
```bash
ssh root@maxhive.cloud "/root/openasset_club/scripts/stop.sh"
sleep 2
ssh root@maxhive.cloud "/root/openasset_club/scripts/start.sh"
```

**Wait 5 seconds, then check logs again:**
```bash
ssh root@maxhive.cloud "tail -50 /root/openasset_club/telegram_bot/logs/bot.log"
```

---

### **STEP 3: Check Python Packages**

Run this:
```bash
ssh root@maxhive.cloud << 'EOF'
python3 << 'PYEOF'
try:
    import telegram
    print(f"✅ telegram: {telegram.__version__}")
except Exception as e:
    print(f"❌ telegram: {e}")

try:
    from telegram.ext import Application
    print("✅ telegram.ext available")
except Exception as e:
    print(f"❌ telegram.ext: {e}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv available")
except Exception as e:
    print(f"❌ python-dotenv: {e}")
PYEOF
EOF
```

**If any fail, you need to install:**
```bash
ssh root@maxhive.cloud "pip install python-telegram-bot==20.3 python-dotenv qrcode pillow"
```

---

### **STEP 4: Verify .env File**

Run this:
```bash
ssh root@maxhive.cloud "cat /root/openasset_club/config/.env"
```

**Check:**
- ✅ TELEGRAM_BOT_TOKEN is set
- ✅ BITCOIN_ADDRESS is set
- ✅ ETHEREUM_ADDRESS is set
- ✅ USDT_ADDRESS is set
- ✅ BNB_ADDRESS is set
- ✅ DASHBOARD_URL is set

**If .env is empty or wrong**, run:
```bash
ssh root@maxhive.cloud << 'EOF'
cat > /root/openasset_club/config/.env << 'ENVEOF'
TELEGRAM_BOT_TOKEN=8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
BITCOIN_ADDRESS=13EVpMB2isjBKVTcWDTJUnoXYvU4Nxy1aB
ETHEREUM_ADDRESS=0x1ee75a52170b17b37184d52cd7fad47551856671
USDT_ADDRESS=TMLcCNSaLpUHxbUC1xE7SuGqZXXkRSgnAo
BNB_ADDRESS=0x1ee75a52170b17b37184d52cd7fad47551856671
DASHBOARD_URL=http://72.62.254.237:8000
CHAT_ID=5587885687
ENVEOF
echo "✅ .env file recreated!"
EOF
```

---

### **STEP 5: Test Bot Startup Manually**

Run the bot directly (not as background process):
```bash
ssh root@maxhive.cloud "cd /root/openasset_club && timeout 15 python3 telegram_bot/main.py"
```

**Watch the output! It should show:**
```
============================================================
🤖 OpenAsset Club Bot Starting...
============================================================
✅ Telegram imported successfully
✅ python-dotenv imported successfully
Loading .env from: /root/openasset_club/config/.env
Bot token loaded: 8806957280:AAGMOvWRllb...
✅ Configuration loaded
   Wallets: 4 configured
   Bots: 8 configured
   Dashboard: http://72.62.254.237:8000
✅ User database loaded: 0 users
============================================================
🚀 STARTING BOT POLLING...
============================================================
✅ Application created
✅ Handlers registered
✅ Starting polling...
✅ Bot is LIVE and listening!
```

**If it stops or shows errors, send me the error output!**

---

### **STEP 6: Full System Restart**

If all above looks good:

```bash
ssh root@maxhive.cloud << 'EOF'
echo "🛑 Stopping all services..."
pkill -f main.py
pkill -f "http.server"
sleep 2

echo "🚀 Starting all services..."
/root/openasset_club/scripts/start.sh

sleep 3

echo "📊 Status check..."
ps aux | grep -E 'main.py|http.server' | grep -v grep

echo "📝 Logs..."
tail -20 /root/openasset_club/telegram_bot/logs/bot.log
EOF
```

---

## 📱 **AFTER FIXES: TEST BOT**

Send to @openasset_club_bot:
```
/start
```

**Should show:**
```
🤖 OpenAsset Club Bot

Welcome! Choose what to do:

[🤖 View Bots] [💰 Payment] [📊 Dashboard] [❓ Help]
```

**Try each button:**
- Click "🤖 View Bots" → Shows all 8 bots ✅
- Click "💰 Payment" → Shows 4 crypto options ✅
- Click "₿ Bitcoin" → Shows wallet address ✅
- Click "◀️ Back" → Returns to menu ✅

---

## 🆘 **IF STILL NOT WORKING**

Send me:

1. **Bot logs:**
   ```bash
   ssh root@maxhive.cloud "tail -100 /root/openasset_club/telegram_bot/logs/bot.log"
   ```

2. **.env file content:**
   ```bash
   ssh root@maxhive.cloud "cat /root/openasset_club/config/.env"
   ```

3. **Python package test:**
   ```bash
   ssh root@maxhive.cloud "python3 -c 'import telegram; print(telegram.__version__)'"
   ```

4. **Manual startup output (first 50 lines):**
   ```bash
   ssh root@maxhive.cloud "timeout 15 python3 /root/openasset_club/telegram_bot/main.py 2>&1 | head -50"
   ```

**Paste all outputs and I'll fix it!** 💪

---

## 🎊 COMMON SOLUTIONS

**Bot token invalid:**
- Get new token from @BotFather
- Make sure token matches in .env

**Missing packages:**
```bash
ssh root@maxhive.cloud "pip install python-telegram-bot==20.3 python-dotenv qrcode pillow requests"
```

**Port 8000 in use:**
```bash
ssh root@maxhive.cloud "lsof -i :8000" 
# Then kill that process
ssh root@maxhive.cloud "pkill -f http.server"
```

**Permission errors:**
```bash
ssh root@maxhive.cloud "chmod -R 755 /root/openasset_club"
ssh root@maxhive.cloud "chown -R root:root /root/openasset_club"
```

---

**Do this NOW:**
1. Replace main.py with main_SIMPLE.py
2. Restart bot
3. Check logs
4. Send me the logs if it doesn't work

Let's get this working! 🚀
