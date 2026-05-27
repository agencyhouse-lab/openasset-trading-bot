# ⚡ QUICK COPY-PASTE COMMANDS FOR SUNNY

Just copy and paste these commands. Takes 30 minutes!

---

## 🚀 START DEPLOYMENT NOW

### **Command 1: SSH into VPS**

```bash
ssh root@maxhive.cloud
```

---

### **Command 2: Create .env file**

```bash
cat > /root/.env << 'EOF'
TELEGRAM_BOT_TOKEN=8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
CHAT_ID=5587885687
MASTER_CHAT_ID=5587885687
DASHBOARD_URL=http://72.62.254.237:8000/trading_dashboard.html
BOT_NAME=openasset_club_bot
VPS_IP=72.62.254.237
DASHBOARD_PORT=8000
EOF
```

**Verify:**
```bash
cat /root/.env
```

---

### **Command 3: Install Dependencies**

```bash
pip install python-telegram-bot==20.3 qrcode pillow python-dotenv requests
```

---

### **Command 4: Create Payment Bot File**

Copy this entire Python code and paste:

```bash
nano /root/telegram_bot_crypto_payments.py
```

Then:
1. Paste entire code
2. Press Ctrl+X
3. Press Y
4. Press Enter

(Or use your SCP to upload the file)

---

### **Command 5: Create Dashboard File**

Copy this entire HTML code and paste:

```bash
nano /root/trading_dashboard.html
```

Then:
1. Paste entire code
2. Press Ctrl+X
3. Press Y
4. Press Enter

(Or use your SCP to upload the file)

---

### **Command 6: Test Bot Locally**

```bash
cd /root
python3 telegram_bot_crypto_payments.py
```

**Expected:**
```
✅ Bot started!
```

**Then press Ctrl+C to stop**

---

### **Command 7: Deploy Bot (24/7)**

```bash
pkill -f telegram_bot_crypto_payments
sleep 2
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
sleep 2
ps aux | grep telegram_bot_crypto_payments
```

**Should show bot running!**

---

### **Command 8: Deploy Dashboard Server (24/7)**

```bash
pkill -f "http.server"
sleep 2
cd /root
nohup python3 -m http.server 8000 > /root/dashboard_server.log 2>&1 &
sleep 2
ps aux | grep "http.server"
```

**Should show server running!**

---

### **Command 9: Check Logs**

```bash
tail -50 /root/bot_payment.log
tail -50 /root/dashboard_server.log
```

---

## ✅ AFTER DEPLOYMENT

### **Test in Telegram:**

Open Telegram and send to **@openasset_club_bot**:

```
/start
```

Should get main menu! ✅

---

### **Test /payment:**

```
/payment
```

Should show crypto options! ✅

---

### **Test /guide:**

```
/guide
```

Should show user guide! ✅

---

### **Test Dashboard:**

Open browser:
```
http://72.62.254.237:8000/trading_dashboard.html
```

Should see beautiful dashboard! ✅

---

## 🎯 ALL DONE? DO THIS:

### **Restart Everything (if needed):**

```bash
# Kill both
pkill -f telegram_bot_crypto_payments
pkill -f "http.server"

# Wait
sleep 3

# Start bot
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &

# Start dashboard
cd /root
nohup python3 -m http.server 8000 > /root/dashboard_server.log 2>&1 &

# Verify both running
echo "Bot status:"
ps aux | grep telegram_bot_crypto_payments | grep -v grep

echo "Dashboard status:"
ps aux | grep "http.server" | grep -v grep
```

---

## 🚀 GO LIVE!

Post in **@openassetclub_updates**:

```
🤖 OPENASSET CLUB BOT IS LIVE!

Remove emotions. Let AI trade.

Bot: @openasset_club_bot
Command: /start

✅ 8 trading bots
✅ Real-time dashboard
✅ Crypto payments
✅ Transparent results

Start now → @openasset_club_bot
```

---

## 📞 QUICK REFERENCE

| Need | Command |
|------|---------|
| Check bot running | `ps aux \| grep telegram_bot_crypto_payments` |
| Check dashboard running | `ps aux \| grep "http.server"` |
| View bot logs | `tail -50 /root/bot_payment.log` |
| Restart bot | `pkill -f telegram_bot_crypto_payments && sleep 2 && nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &` |
| Restart dashboard | `pkill -f "http.server" && sleep 2 && cd /root && nohup python3 -m http.server 8000 > /root/dashboard_server.log 2>&1 &` |

---

## ⏱️ TOTAL TIME

- Preparation: 5 min
- Installation: 10 min
- Deployment: 10 min
- Testing: 5 min

**TOTAL: 30 minutes!**

---

**Ready? Start with Command 1!** 🚀

Good luck, Sunny! 💪
