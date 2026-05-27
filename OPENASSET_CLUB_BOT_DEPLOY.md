# 🤖 OPENASSET_CLUB_BOT - DEPLOYMENT GUIDE

**Bot Name:** openasset_club_bot  
**Bot Token:** 8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU  
**User ID:** 5587885687  
**Dashboard:** http://72.62.254.237:8000/trading_dashboard.html

---

## 🎯 TODAY'S DEPLOYMENT (30 minutes)

### **STEP 1: Connect to VPS (1 min)**

On your laptop, open terminal and run:

```bash
ssh root@maxhive.cloud
```

You should now be in VPS terminal. All commands below run in VPS!

---

### **STEP 2: Create .env File (2 min)**

Copy this ENTIRE section and paste into VPS terminal:

```bash
cat > /root/.env << 'EOF'
TELEGRAM_BOT_TOKEN=8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
CHAT_ID=5587885687
MASTER_CHAT_ID=5587885687
BOT_NAME=openasset_club_bot
DASHBOARD_URL=http://72.62.254.237:8000/trading_dashboard.html
DASHBOARD_PORT=8000
VPS_IP=72.62.254.237
BITCOIN_ADDRESS=YOUR_BITCOIN_ADDRESS_HERE
ETHEREUM_ADDRESS=YOUR_ETHEREUM_ADDRESS_HERE
USDT_ADDRESS=YOUR_USDT_ADDRESS_HERE
BNB_ADDRESS=YOUR_BNB_ADDRESS_HERE
BOT_TIMEOUT=30
ALERT_FREQUENCY=hourly
EOF
```

**Expected output:** Nothing (file created silently)

**Verify:**
```bash
cat /root/.env
```

Should show your configuration above. ✅

---

### **STEP 3: Install Dependencies (3 min)**

```bash
pip install python-telegram-bot qrcode pillow python-dotenv
```

**Wait for it to finish...**

**Expected output:**
```
Successfully installed python-telegram-bot qrcode pillow python-dotenv
```

✅ Done!

---

### **STEP 4: Upload Bot Files (2 min)**

**On your laptop** (new terminal, NOT in VPS):

```bash
# Navigate to where you have the files
cd ~/Documents/Sunny_Trading_Bot/Code/

# Upload bot file
scp telegram_bot_crypto_payments.py root@maxhive.cloud:/root/

# Upload dashboard file
scp trading_dashboard.html root@maxhive.cloud:/root/
```

**Expected:** No output = success ✅

**Verify in VPS:**
```bash
ls -lah /root/telegram_bot_crypto_payments.py
ls -lah /root/trading_dashboard.html
```

Should show both files. ✅

---

### **STEP 5: Test Bot (5 min)**

In VPS terminal:

```bash
python3 /root/telegram_bot_crypto_payments.py
```

**Expected output:**
```
🤖 AI TRADING BOT WITH CRYPTO PAYMENTS
Remove Human Psychology | Crypto Only
✅ Bot started!
Commands:
  /start   - Main menu
  /payment - Crypto payment options
  /guide   - User guide
  /bots    - Available bots
  /help    - Get help
```

**Test in Telegram:**
- Open Telegram
- Search for: **@openasset_club_bot**
- Send: `/start`
- Should see main menu! ✅

**Stop test:**
```
Press Ctrl+C in terminal
```

---

### **STEP 6: Deploy Bot (24/7)**

Keep bot running in background:

```bash
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
```

**Verify it's running:**
```bash
ps aux | grep telegram_bot_crypto_payments
```

Should show 1 process running. ✅

---

### **STEP 7: Start Dashboard Server (5 min)**

**Open a NEW terminal on VPS** (keep other one for monitoring):

```bash
cd /root
python3 -m http.server 8000
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8000
```

**Keep this terminal OPEN!** (Don't press Ctrl+C)

**Test dashboard in browser:**
```
http://72.62.254.237:8000/trading_dashboard.html
```

Should load beautiful dashboard! ✅

---

### **STEP 8: Update Crypto Wallets (5 min)**

**IMPORTANT:** Add your wallet addresses!

In first VPS terminal:

```bash
nano /root/telegram_bot_crypto_payments.py
```

Find this section (around line 50):

```python
CRYPTO_WALLETS = {
    "Bitcoin": {
        "address": "1A1z7agoat2YrQQ98XWwxvVHUYkpqB",  # ← REPLACE THIS
        ...
    },
    "Ethereum": {
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f5dD8b",  # ← REPLACE THIS
        ...
    },
    ...
}
```

**Replace the 4 addresses with YOUR wallet addresses:**

```python
"Bitcoin": {
    "address": "YOUR_ACTUAL_BTC_ADDRESS",
    ...
},
"Ethereum": {
    "address": "YOUR_ACTUAL_ETH_ADDRESS",
    ...
},
"USDT": {
    "address": "YOUR_ACTUAL_USDT_ADDRESS",
    ...
},
"Binance Coin": {
    "address": "YOUR_ACTUAL_BNB_ADDRESS",
    ...
}
```

**Save:**
- Press: `Ctrl+X`
- Press: `Y`
- Press: `Enter`

**Restart bot:**
```bash
pkill -f telegram_bot_crypto_payments
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
```

---

### **STEP 9: Complete Test in Telegram (10 min)**

Send these commands to **@openasset_club_bot**:

```
/start
```
**Expected:** Main menu with buttons ✅

```
/bots
```
**Expected:** All 8 bots with pricing ✅

```
/payment
```
**Expected:** 4 crypto options (Bitcoin, Ethereum, USDT, BNB) ✅

```
Click: [₮ USDT]
```
**Expected:** Your wallet address + QR code ✅

```
/guide
```
**Expected:** Complete user guide ✅

```
/dashboard
```
**Expected:** Opens dashboard URL ✅

---

## ✅ VERIFICATION CHECKLIST

After all steps, verify:

```bash
# Check bot is running
ps aux | grep telegram_bot_crypto_payments
# Should show: python3 /root/telegram_bot_crypto_payments.py

# Check dashboard is running
ps aux | grep http.server
# Should show: python3 -m http.server 8000

# Check logs for errors
tail -50 /root/bot_payment.log
# Should show no errors

# Check .env has your token
cat /root/.env | grep TELEGRAM_BOT_TOKEN
# Should show your token
```

**All green?** 🎉 **YOU'RE READY!**

---

## 📱 USER EXPERIENCE

Now when users find your bot:

```
1. They /start → See main menu
2. They /bots → See 8 trading bots with prices
3. They /payment → See crypto wallet addresses + QR codes
4. They scan QR and send crypto
5. Bot shows: "✅ Payment confirmed! Bot activated!"
6. They /dashboard → See real trades
```

**Simple. Automated. Pure crypto.**

---

## 🔧 MAINTENANCE

### Daily:
```bash
# Check if bot is still running
ps aux | grep telegram_bot_crypto_payments

# If not, restart:
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
```

### Check logs for errors:
```bash
tail -100 /root/bot_payment.log
```

### Stop bot if needed:
```bash
pkill -f telegram_bot_crypto_payments
```

---

## 🆘 TROUBLESHOOTING

### Bot won't start?
```bash
# Check token in .env
cat /root/.env | grep TELEGRAM_BOT_TOKEN

# Test directly
python3 /root/telegram_bot_crypto_payments.py

# Look for error message
```

### Dashboard won't load?
```bash
# Make sure server is running
ps aux | grep http.server

# If not, start it:
cd /root && python3 -m http.server 8000 &

# Wait 5 seconds, try browser again
```

### QR codes not generating?
```bash
# Install library
pip install qrcode pillow

# Restart bot
pkill -f telegram_bot_crypto_payments
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
```

### Wallet addresses showing as 000... in config?
```bash
# Make sure you actually updated the addresses!
nano /root/telegram_bot_crypto_payments.py
# Find CRYPTO_WALLETS section and verify YOUR addresses are there
```

---

## 📊 NEXT STEPS

### Week 1: Ready ✅
- Bot deployed ✅
- Dashboard online ✅
- Wallets configured ✅

### Week 2: Beta Test
- Invite 5-10 friends
- Have them test /start, /payment, /guide
- Get feedback

### Week 3: Optimize
- Refine guides
- Perfect user experience
- Create marketing message

### Week 4: Launch
- Announce bot publicly
- Invite first paying users
- Start earning! 💰

---

## 🎊 SUCCESS!

Your bot is now:
- ✅ Live on Telegram (@openasset_club_bot)
- ✅ Accepting crypto payments
- ✅ Showing professional dashboard
- ✅ Ready for users

**Now invite your first 10 users!**

---

**Questions? Feel free to ask!** 👋

**Ready to test? Let me know when bot is running!** 🚀
