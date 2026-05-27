# 🚀 MASTER BOT CONTROLLER - DEPLOYMENT PLAN

**Goal:** Control ALL 8 trading bots from ONE Telegram bot

**Time Required:** 15-30 minutes

---

## 📥 What You Got

| File | Purpose |
|------|---------|
| **master_bot_controller.py** | The main bot - controls all 8 bots |
| **bot_manager.sh** | Bash script to manage everything |
| **vps_bot_diagnostic.py** | Check if your VPS is set up correctly |
| **MASTER_BOT_SETUP.md** | Detailed setup guide |

---

## ✅ STEP-BY-STEP SETUP

### **Step 1: Check Your VPS Setup** ⏱️ 5 min

SSH into your VPS:

```bash
ssh root@maxhive.cloud
```

Run diagnostic:

```bash
python3 vps_bot_diagnostic.py
```

**You should see:**
- ✅ Python installed
- ✅ Bot files found
- ✅ Bot status (running/not running)

**If something is RED:**
- Check: `ls -la /root/trading_bots_deployed/`
- Check: `ps aux | grep python3`
- Diagnose: Follow suggestions in diagnostic output

---

### **Step 2: Create/Update .env File** ⏱️ 2 min

Open nano:

```bash
nano /root/.env
```

Add these lines:

```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
CHAT_ID=5587885687
```

**Getting BOT_TOKEN:**
1. Open Telegram
2. Search: `@BotFather`
3. Type: `/newbot`
4. Choose name: "Master Trading Bot"
5. Choose username: `@your_master_bot`
6. Copy TOKEN

Save: Press `Ctrl+X`, then `Y`, then Enter

---

### **Step 3: Upload Master Bot Files** ⏱️ 5 min

On your VPS, copy these files to `/root/`:

```bash
# Copy from downloads/wherever you have them
cp master_bot_controller.py /root/
cp bot_manager.sh /root/
cp vps_bot_diagnostic.py /root/

# Make bot manager executable
chmod +x /root/bot_manager.sh
```

Verify files are there:

```bash
ls -la /root/*.py /root/*.sh
```

---

### **Step 4: Install Dependencies** ⏱️ 3 min

Use the bot manager script:

```bash
bash /root/bot_manager.sh install
```

This installs:
- python-telegram-bot
- python-binance
- alpaca-trade-api
- requests
- python-dotenv

Or install manually:

```bash
pip install python-telegram-bot python-dotenv
```

---

### **Step 5: Test Master Bot** ⏱️ 2 min

Run it in foreground (so you see errors):

```bash
python3 /root/master_bot_controller.py
```

**You should see:**
```
🤖  MASTER BOT CONTROLLER STARTING
✅ Bot started! Listening for commands...
📱 Chat ID: 5587885687
🤖 Managing 8 bots
```

Press `Ctrl+C` to stop.

---

### **Step 6: Run in Background** ⏱️ 2 min

Start and keep running 24/7:

```bash
# Using bot_manager.sh (EASIEST):
bash /root/bot_manager.sh start_master

# Or manually:
nohup python3 /root/master_bot_controller.py > /root/master_bot.log 2>&1 &
```

Verify it's running:

```bash
ps aux | grep master_bot
```

You should see one process running.

---

### **Step 7: Test in Telegram** ⏱️ 1 min

Open your Telegram and send:

```
/start
```

to your `@your_master_bot`

**You should see:**
```
🤖 MASTER BOT CONTROLLER

Available bots:
├ 🔵 ATBOT (Alpaca Live)
├ 🔴 BTBOT (Binance Live)
├ 🟠 ETBOT (eToro Crypto)
├ 🟡 BOT1-5 (5 Paper Trading Bots)

[View All Status] [Control Panel] [Detailed Stats] [Settings] [Help]
```

🎉 **YOU'RE DONE!**

---

## 🎮 NOW USE IT

### **View All Bots Status**

Send to bot:

```
/status
```

Returns:

```
🤖 MASTER BOT STATUS

🟢 ATBOT
   └ Alpaca Live Trading
🔴 BTBOT
   └ Binance Live Trading (RSI)
... etc
```

### **Start a Bot**

Send to bot:

```
/start_bot BTBOT
```

Returns:

```
✅ BTBOT started successfully
```

### **Stop a Bot**

Send to bot:

```
/stop_bot BOT1
```

### **Restart a Bot**

Send to bot:

```
/restart_bot ETBOT
```

### **View Logs**

Send to bot:

```
/logs BOT1
```

Shows last 20 lines of logs.

### **Using Buttons (GUI)**

Send: `/start`

Then click:
- **View All Status** → See all bots
- **Control Panel** → Pick bot to control
- **Detailed Stats** → Advanced info
- **Settings** → Configuration

---

## 🔧 QUICK BOT MANAGER COMMANDS

Instead of typing to Telegram, use bash script:

```bash
# View all status
bash /root/bot_manager.sh status

# Start master bot
bash /root/bot_manager.sh start_master

# Stop master bot
bash /root/bot_manager.sh stop_master

# Restart master bot
bash /root/bot_manager.sh restart_master

# View logs
bash /root/bot_manager.sh logs master

# Quick start (everything)
bash /root/bot_manager.sh quickstart
```

---

## 🚨 TROUBLESHOOTING

### **Bot Not Responding?**

Check if running:

```bash
ps aux | grep master_bot
```

If NOT running, start it:

```bash
python3 /root/master_bot_controller.py
```

Check logs:

```bash
tail -50 /root/master_bot.log
```

### **Token Error?**

Check .env file:

```bash
cat /root/.env
```

Make sure:
- BOT_TOKEN starts with numbers (e.g., `123456:ABC`)
- CHAT_ID is `5587885687` (or your actual chat ID)
- No quotes around values

### **Trading Bot Not Starting?**

Check if file exists:

```bash
ls -la /root/trading_bots_deployed/bot1_crypto.py
```

Check permissions:

```bash
chmod +x /root/trading_bots_deployed/bot*.py
```

Check manually:

```bash
cd /root/trading_bots_deployed
python3 bot1_crypto.py
```

---

## 📋 TYPICAL DAILY WORKFLOW

### **Morning**
```
/status                    ← Check all bots
/start_bot BTBOT          ← Start BTBOT
/start_bot BOT1           ← Start BOT1
```

### **Monitor**
```
/logs BTBOT               ← Check what BTBOT is doing
/logs BOT1                ← Check BOT1 trades
```

### **Troubleshoot**
```
/stop_bot BOT1            ← Stop if issues
/restart_bot BOT1         ← Restart
/logs BOT1                ← Check new logs
```

### **Close**
```
/stop_bot BTBOT           ← Stop BTBOT
/stop_bot BOT1            ← Stop BOT1
```

---

## 🎯 ADVANCED: Make It Auto-Start on Reboot

So master bot starts automatically if VPS restarts:

```bash
bash /root/bot_manager.sh systemd
```

Then:

```bash
sudo systemctl start master-bot
sudo systemctl status master-bot
```

Now it will auto-start! 🎉

---

## 📊 FILE LOCATIONS

Keep track of where everything is:

```
/root/master_bot_controller.py       ← Main bot
/root/bot_manager.sh                 ← Management script
/root/vps_bot_diagnostic.py          ← Diagnostic tool
/root/.env                           ← Your tokens

/root/master_bot.log                 ← Bot logs
/root/trading_bots.log               ← Trading bot logs

/root/trading_bots_deployed/         ← BOT1-5
/root/btbot/                         ← BTBOT
/root/ps1trade/                      ← ETBOT
/root/trading_bot/                   ← ATBOT
```

---

## ✅ FINAL CHECKLIST

After setup, verify:

- [ ] Master bot running: `ps aux | grep master_bot`
- [ ] Responds to /start: ✅ Works
- [ ] /status shows all bots: ✅ Works
- [ ] Can start bot: /start_bot BOT1 works
- [ ] Can stop bot: /stop_bot BOT1 works
- [ ] Can view logs: /logs BOT1 shows content
- [ ] Bot manager script works: `bash bot_manager.sh status`

---

## 🎓 WHAT YOU NOW HAVE

✅ **ONE Telegram bot** controlling 8 trading bots
✅ **Start/stop/restart** any bot from phone
✅ **View logs** in real-time
✅ **Complete automation** management

No more SSH or web server headaches!

---

## 🚀 YOU'RE READY!

**Next:** Open Telegram, send `/start` to your bot, and enjoy! 🎉

Questions? Check:
1. Logs: `tail -50 /root/master_bot.log`
2. Diagnostic: `python3 /root/vps_bot_diagnostic.py`
3. Status: `bash /root/bot_manager.sh status`

---

## 🎬 QUICK START (COPY-PASTE)

If you want to do everything NOW, just run this:

```bash
ssh root@maxhive.cloud

# Run all setup at once
bash /root/bot_manager.sh quickstart
```

This will:
1. Check VPS ✅
2. Install dependencies ✅
3. Create .env ✅
4. Setup systemd ✅
5. Start master bot ✅
6. Start all trading bots ✅

**Done in ~5 minutes!**

---

**Questions? Start simple: Just run `/start` in Telegram!** 🤖
