# 🚀 OPENASSET CLUB BOT - ONE-COMMAND FIX

## The Problem
- ❌ .env has wrong token
- ❌ main.py is old initializer script
- ❌ Bot doesn't respond to /start

## The Solution

### **JUST RUN THIS ONE COMMAND:**

```bash
ssh root@maxhive.cloud << 'DEPLOY'
cat > /root/deploy.sh << 'SCRIPT'
#!/bin/bash
# Auto-generated deploy script

# Fix .env
cat > /root/openasset_club/config/.env << 'EOF'
TELEGRAM_BOT_TOKEN=8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
BITCOIN_ADDRESS=13EVpMB2isjBKVTcWDTJUnoXYvU4Nxy1aB
ETHEREUM_ADDRESS=0x1ee75a52170b17b37184d52cd7fad47551856671
USDT_ADDRESS=TMLcCNSaLpUHxbUC1xE7SuGqZXXkRSgnAo
BNB_ADDRESS=0x1ee75a52170b17b37184d52cd7fad47551856671
DASHBOARD_URL=http://72.62.254.237:8000
CHAT_ID=5587885687
EOF

# Kill old bot
pkill -f main.py || true
pkill -f http.server || true
sleep 1

# Restart
/root/openasset_club/scripts/start.sh

sleep 3
echo "✅ Bot restarted! Check logs..."
tail -30 /root/openasset_club/telegram_bot/logs/bot.log
SCRIPT

chmod +x /root/deploy.sh
/root/deploy.sh
DEPLOY
```

---

## 📱 Test After 1 Minute

Send to **@openasset_club_bot**:
```
/start
```

Should show menu with buttons!

---

## 🎯 If That Doesn't Work

Check bot logs:
```bash
ssh root@maxhive.cloud "tail -50 /root/openasset_club/telegram_bot/logs/bot.log"
```

Send me the output and I'll fix it!

---

That's it, Sunny! ONE command and your bot is fixed! 🎉
