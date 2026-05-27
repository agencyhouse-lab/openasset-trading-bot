# 🚀 DEPLOY BOTH BOTS - USER BOT + ADMIN BOT

## ⚙️ WHAT'S NEW

✅ **Fixed Back Buttons** - Now works perfectly
✅ **Trading Platforms** - Binance, Alpaca, eToro, Exness
✅ **Admin Bot Separation** - Notifications go to admin bot
✅ **Auto-API Storage** - Keys saved automatically
✅ **30-Day Expiry** - Subscriptions auto-expire
✅ **Revenue Dashboard** - Admin can see stats

---

## 📋 BOT TOKENS & IDs

```
USER BOT:
- Token: 8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
- Handle: @openasset_club_bot
- File: bot_user_final.py

ADMIN BOT:
- Token: 8759490386:AAGy3QzviccZzRkXHYmD7EHYtICvToQO3yU
- Handle: @openasset_admin_bot
- File: bot_admin.py

ADMIN USER ID: 5587885687
```

---

## 🔧 DEPLOYMENT STEPS

### **STEP 1: Stop Old Bot**

```bash
ssh root@72.62.254.237

# Kill old bot
pkill -9 -f "main.py"
sleep 2

# Backup old
cp /root/openasset_club/telegram_bot/main.py /root/openasset_club/telegram_bot/main.py.old
```

### **STEP 2: Deploy USER BOT**

```bash
cd /root/openasset_club/telegram_bot

# Create new user bot (copy entire content of bot_user_final.py)
cat > main.py << 'EOF'
[PASTE THE ENTIRE bot_user_final.py CONTENT HERE]
EOF

# Start user bot
chmod +x main.py
nohup python3 main.py > logs/user_bot.log 2>&1 &
sleep 2

# Verify
ps aux | grep "python3 main.py" | grep -v grep && echo "✅ USER BOT RUNNING!"
```

### **STEP 3: Deploy ADMIN BOT**

```bash
# Create admin bot file
mkdir -p /root/openasset_admin_bot
cd /root/openasset_admin_bot

# Create admin bot (copy entire content of bot_admin.py)
cat > admin_bot.py << 'EOF'
[PASTE THE ENTIRE bot_admin.py CONTENT HERE]
EOF

# Create logs directory
mkdir -p logs

# Start admin bot
chmod +x admin_bot.py
nohup python3 admin_bot.py > logs/admin_bot.log 2>&1 &
sleep 2

# Verify
ps aux | grep "python3 admin_bot.py" | grep -v grep && echo "✅ ADMIN BOT RUNNING!"
```

### **STEP 4: Verify Both Running**

```bash
# Check both bots
ps aux | grep python3 | grep -E "(main.py|admin_bot.py)"

# Should show:
# root ... python3 main.py (USER BOT)
# root ... python3 admin_bot.py (ADMIN BOT)

# Check logs
tail -20 /root/openasset_club/telegram_bot/logs/user_bot.log
tail -20 /root/openasset_admin_bot/logs/admin_bot.log
```

---

## 🧪 TEST THE SETUP

### **Test User Bot**

1. **Open Telegram**
2. **Go to:** @openasset_club_bot
3. **Send:** `/start`

Should see beautiful launch screen! ✨

### **Test Admin Bot**

1. **Open Telegram**
2. **Go to:** @openasset_admin_bot
3. **Send:** `/start`

Should see admin menu with options!

### **Test Payment Flow**

1. **As User:** Go through subscription flow
2. **Send Payment:** Click "Payment Sent"
3. **As Admin:** Check admin bot for notification
4. **Admin Approves:** Click approve button
5. **User Gets:** Instant activation message

### **Test API Linking**

1. **As User:** Click Trading → Select Platform
2. **Send API Key:** Type key
3. **As Admin:** Get notification in admin bot
4. **User Confirms:** Gets "Account Connected" message

---

## 📊 HOW THE BOTS COMMUNICATE

```
USER BOT (openasset_club_bot)
    ↓ (User subscribes & sends API keys)
    ↓
ADMIN BOT (openasset_admin_bot)
    ↓ (Admin approves/rejects)
    ↓
USER BOT (Sends confirmation to user)
```

**Flow:**
1. User sends payment → User Bot stores it
2. User Bot notifies Admin Bot
3. Admin clicks approve in Admin Bot
4. Admin Bot updates databases
5. User Bot notifies user of approval
6. User can now trade!

---

## 🔄 AUTO-RESTART ON REBOOT

Add to crontab to restart bots on system reboot:

```bash
crontab -e

# Add these lines:
@reboot sleep 10 && cd /root/openasset_club/telegram_bot && nohup python3 main.py > logs/user_bot.log 2>&1 &
@reboot sleep 15 && cd /root/openasset_admin_bot && nohup python3 admin_bot.py > logs/admin_bot.log 2>&1 &
```

---

## 📁 FILE STRUCTURE AFTER DEPLOYMENT

```
/root/
├── openasset_club/
│   └── telegram_bot/
│       ├── main.py (USER BOT)
│       ├── logs/
│       │   ├── user_bot.log
│       │   └── bot.log
│       ├── database/
│       │   ├── subscriptions.json
│       │   ├── payments.json
│       │   ├── accounts.json
│       │   └── ...
│       └── config/
│           └── .env
│
└── openasset_admin_bot/
    ├── admin_bot.py (ADMIN BOT)
    └── logs/
        └── admin_bot.log
```

---

## ✅ FEATURES CHECKLIST

```
USER BOT (@openasset_club_bot):
✅ Beautiful launch screen
✅ Fixed back buttons (WORKING!)
✅ Subscription plans
✅ Crypto payments
✅ Trading platform selection
✅ Platform-specific API guides
✅ API key input (2-step)
✅ View balances/positions/stats
✅ 30-day auto-expiry
✅ User guide & help

ADMIN BOT (@openasset_admin_bot):
✅ Admin menu
✅ Pending payments list
✅ Approve/reject payments
✅ View API submissions
✅ Active users list
✅ Revenue statistics
✅ Admin statistics
✅ Auto-notifications from user bot
✅ Payment auto-approval flow
✅ API key notifications
```

---

## 💡 HOW IT WORKS

### **User Subscribes:**
```
1. User sends /start to @openasset_club_bot
2. User clicks "Subscribe Now"
3. User chooses plan & sends crypto payment
4. User clicks "Payment Sent"
5. User Bot sends notification to @openasset_admin_bot
6. Admin gets message with approve button
```

### **Admin Approves:**
```
1. Admin opens @openasset_admin_bot
2. Admin clicks /start
3. Admin clicks "Pending Payments"
4. Admin clicks "✅ APPROVE" button
5. User Bot automatically:
   - Activates 30-day subscription
   - Sends confirmation to user
   - Unlocks all features
```

### **User Links API:**
```
1. User clicks Trading → Select Platform
2. User clicks "📖 API Guide"
3. User follows guide & gets API key
4. User sends API key to bot
5. Bot asks for secret key
6. User sends secret key
7. Bot stores both encrypted
8. Admin Bot gets notification
9. Bot shows "✅ Connected!"
10. User can now trade
```

---

## 🔐 SECURITY

✅ API keys stored encrypted in JSON
✅ Only bot can access keys
✅ Users can revoke anytime
✅ Admin bot only accessible to you
✅ 30-day auto-expiry prevents old subscriptions
✅ All payments logged with timestamps

---

## 📊 MONITORING

### **Check User Bot:**
```bash
tail -f /root/openasset_club/telegram_bot/logs/user_bot.log
```

### **Check Admin Bot:**
```bash
tail -f /root/openasset_admin_bot/logs/admin_bot.log
```

### **View Payments:**
```bash
cat /root/openasset_club/telegram_bot/database/payments.json | python3 -m json.tool
```

### **View Subscriptions:**
```bash
cat /root/openasset_club/telegram_bot/database/subscriptions.json | python3 -m json.tool
```

### **View API Keys:**
```bash
cat /root/openasset_club/telegram_bot/database/accounts.json | python3 -m json.tool
```

---

## 🚀 YOU'RE NOW RUNNING

✅ **User-facing bot** for trading & subscriptions
✅ **Admin bot** for approvals & management
✅ **Automated payment flow** 
✅ **Secure API key handling**
✅ **30-day subscriptions** with auto-expiry
✅ **Professional trading platform**

---

## 📞 TROUBLESHOOTING

**Bot not responding?**
```bash
ps aux | grep python3
# If bot not in list, restart:
pkill -9 -f "main.py"
cd /root/openasset_club/telegram_bot
nohup python3 main.py > logs/user_bot.log 2>&1 &
```

**Admin bot not receiving notifications?**
```bash
# Check if admin bot is running:
ps aux | grep admin_bot.py

# Check logs:
tail -50 /root/openasset_admin_bot/logs/admin_bot.log
```

**Payments not appearing in admin bot?**
```bash
# Check payments database:
cat /root/openasset_club/telegram_bot/database/payments.json

# Check if payment is marked 'pending':
grep '"status": "pending"' /root/openasset_club/telegram_bot/database/payments.json
```

---

## 🎊 YOU'RE READY TO LAUNCH!

Both bots are now deployed and ready to:
- Accept cryptocurrency payments
- Manage subscriptions automatically
- Handle API keys securely
- Send real-time notifications
- Approve/reject requests from admin panel
- Provide professional trading platform

**Start promoting!** 💰🚀
