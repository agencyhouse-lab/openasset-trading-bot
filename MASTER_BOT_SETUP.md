# 🤖 MASTER BOT CONTROLLER - QUICK SETUP

Control ALL 8 of your trading bots from ONE Telegram bot!

---

## 🎯 What This Does

One Telegram bot that can:
- ✅ See status of all 8 bots (ATBOT, BTBOT, ETBOT, BOT1-5)
- ✅ Start/stop/restart any bot
- ✅ View logs for debugging
- ✅ Manage everything from your phone

---

## ⚡ Quick Start (5 minutes)

### Step 1: Prepare .env File

Create/update `/root/.env`:

```bash
nano /root/.env
```

Add these lines:

```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
CHAT_ID=5587885687
```

**To get BOT_TOKEN:**
1. Open Telegram → Search @BotFather
2. /newbot
3. Choose name: "Master Trading Bot"
4. Choose username: @your_master_bot
5. Copy the TOKEN

### Step 2: Upload Master Bot

SSH into VPS:

```bash
ssh root@maxhive.cloud

# Go to trading bots directory
cd /root

# Copy the master bot file here
# (assuming you have it ready)
```

Or create it directly:

```bash
cat > /root/master_bot_controller.py << 'EOF'
# Paste the entire master_bot_controller.py code here
EOF
```

### Step 3: Install Dependencies

```bash
pip install python-telegram-bot python-dotenv
```

### Step 4: Run It

```bash
# Test first
python3 /root/master_bot_controller.py

# You should see:
# ✅ Bot started! Listening for commands...
# 📱 Chat ID: 5587885687
```

### Step 5: Run in Background (24/7)

Press Ctrl+C to stop, then:

```bash
# Option 1: Use nohup
nohup python3 /root/master_bot_controller.py > master_bot.log 2>&1 &

# Option 2: Use screen
screen -S master_bot
python3 /root/master_bot_controller.py
# Press Ctrl+A then D to detach
```

### Step 6: Test It

Open Telegram, send `/start` to your bot.

You should see the main menu! ✅

---

## 📱 Available Commands

### Menu Buttons (Interactive)
- **View All Status** - See all 8 bots at a glance
- **Control Panel** - Select bot to control
- **Detailed Stats** - Detailed information
- **Settings** - Configuration options

### Text Commands

```
/start                    → Main menu
/status                   → All bots status
/start_bot BOT1          → Start BOT1
/stop_bot BOT1           → Stop BOT1
/restart_bot BOT1        → Restart BOT1
/logs BOT1               → View BOT1 logs (last 20 lines)
```

### Bot Names

```
ATBOT   - Alpaca Live Trading
BTBOT   - Binance Live Trading
ETBOT   - eToro Crypto Watch
BOT1    - Crypto Multi-Asset
BOT2    - Stock Market
BOT3    - Commodities
BOT4    - Forex Pairs
BOT5    - Scalper Crypto
```

### Example Commands

```
/start_bot BTBOT          ← Start BTBOT
/stop_bot BOT1            ← Stop BOT1
/restart_bot ETBOT        ← Restart ETBOT
/logs BOT1                ← View BOT1 logs
/status                   ← See all status
```

---

## 🔧 Troubleshooting

### Bot Not Responding?

**Check if master bot is running:**
```bash
ps aux | grep master_bot
```

**Check logs:**
```bash
tail -50 master_bot.log
```

**Restart master bot:**
```bash
pkill -f master_bot_controller.py
sleep 2
nohup python3 /root/master_bot_controller.py > master_bot.log 2>&1 &
```

### Trading Bots Not Starting?

**Check if files exist:**
```bash
ls -la /root/trading_bots_deployed/
ls -la /root/btbot/
ls -la /root/ps1trade/
```

**Run diagnostic:**
```bash
python3 /root/vps_bot_diagnostic.py
```

**Start bot manually:**
```bash
cd /root/trading_bots_deployed
python3 bot1_crypto.py
```

### "Bot file not found" Error?

Edit `master_bot_controller.py`, update bot paths:

```python
BOTS_CONFIG = {
    "BOT1": {
        "path": "/root/YOUR_ACTUAL_PATH/bot1.py",  # Fix this
        # ...
    }
}
```

---

## 📊 Typical Workflow

### Morning Check

```
/status
```

View all 8 bots status (running/stopped)

### Start Trading

```
/start_bot BTBOT
/start_bot BOT1
/start_bot BOT2
```

### Monitor Performance

```
/logs BTBOT
/logs BOT1
```

View what they're doing

### Troubleshoot Issue

```
/stop_bot BOT1
/restart_bot BOT1
/logs BOT1
```

Stop, restart, check logs

---

## 🚀 Make It Persistent (SystemD)

Create systemd service so bot auto-starts on VPS reboot:

```bash
sudo nano /etc/systemd/system/master-bot.service
```

Paste this:

```ini
[Unit]
Description=Master Trading Bot Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/master_bot_controller.py
Restart=always
RestartSec=10
StandardOutput=append:/root/master_bot.log
StandardError=append:/root/master_bot.log

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable master-bot
sudo systemctl start master-bot
sudo systemctl status master-bot
```

Now master bot restarts automatically if VPS reboots! 🎯

---

## 📈 Advanced: Monitor All Bots

Add this cron job to send daily status:

```bash
crontab -e
```

Add this line:

```
0 8 * * * curl "https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=$(python3 /root/check_all_bots.py)"
```

This sends status every day at 8 AM.

---

## 🔐 Security

1. **Protect .env file:**
   ```bash
   chmod 600 /root/.env
   ```

2. **Limit bot access:**
   Only send commands from your CHAT_ID

3. **Monitor bot logs:**
   ```bash
   tail -f master_bot.log
   ```

---

## 📋 File Locations

All files should be in these locations:

```
/root/master_bot_controller.py        ← Master bot script
/root/.env                            ← Your tokens & configs
/root/master_bot.log                  ← Master bot logs

/root/trading_bots_deployed/          ← BOT1-5 files
/root/btbot/                          ← BTBOT files
/root/ps1trade/                       ← ETBOT files
/root/trading_bot/                    ← ATBOT files
```

---

## ✅ Quick Checklist

After setup, verify:

- [ ] Master bot running: `ps aux | grep master_bot`
- [ ] Can send /start: Bot responds ✅
- [ ] Can see status: /status shows all bots
- [ ] Can start bot: /start_bot BOT1 works
- [ ] Can view logs: /logs BOT1 shows content
- [ ] Systemd enabled: `systemctl status master-bot`

---

## 🎯 Next Steps

1. **Setup complete?** Test with /start
2. **All working?** Start using daily
3. **Want improvements?** Add scheduling, alerts, etc.

---

## 💬 Example Session

```
You: /start
Bot: 🤖 MASTER BOT CONTROLLER
     [View All Status] [Control Panel] ...

You: /status
Bot: 🟢 ATBOT - Alpaca Live
     🔴 BTBOT - Binance Live (stopped)
     🟢 ETBOT - eToro Crypto
     ... etc

You: /start_bot BTBOT
Bot: ✅ BTBOT started successfully

You: /logs BTBOT
Bot: 📋 BTBOT Logs:
     2024-05-27 10:30:01 - Bot started
     2024-05-27 10:30:15 - Connected to API
     2024-05-27 10:31:02 - Found signal on BTC
     ... etc
```

---

## 🆘 Need Help?

**Master bot not starting?**
```bash
python3 /root/master_bot_controller.py
# This will show errors if there are any
```

**Check system:**
```bash
python3 /root/vps_bot_diagnostic.py
# Comprehensive check of all bots
```

**Contact Support:**
- Check logs: `tail -100 master_bot.log`
- Show bot status: `/status`
- Share error message

---

**You're all set! 🚀 Start with /start**
