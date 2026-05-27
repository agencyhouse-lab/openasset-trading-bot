# 🚀 DEPLOY ENHANCED TELEGRAM BOT

Copy and paste this entire command:

```bash
ssh root@maxhive.cloud << 'BOTDEPLOY'

echo "🤖 Deploying Enhanced Telegram Bot..."
echo "======================================"
echo ""

# Create database for reports if not exists
mkdir -p /root/openasset_club/telegram_bot/database
touch /root/openasset_club/telegram_bot/database/reports.json

# Kill old bot
pkill -9 -f "main.py" 2>/dev/null || true
sleep 1

# Create enhanced bot
cat > /root/openasset_club/telegram_bot/main.py << 'BOTEND'
#!/usr/bin/env python3
"""
OpenAsset Club Trading Bot - Enhanced Version
Professional Telegram Bot with Reporting System
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv('/root/openasset_club/config/.env')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://72.62.254.237:8000')

# Database paths
DB_USERS = '/root/openasset_club/telegram_bot/database/users.json'
DB_REPORTS = '/root/openasset_club/telegram_bot/database/reports.json'

# Crypto wallets
CRYPTOS = {
    "btc": ("Bitcoin", "13EVpMB2isjBKVTcWDTJUnoXYvU4Nxy1aB", "₿"),
    "eth": ("Ethereum", "0x1ee75a52170b17b37184d52cd7fad47551856671", "Ξ"),
    "usdt": ("USDT (Tron)", "TMLcCNSaLpUHxbUC1xE7SuGqZXXkRSgnAo", "₮"),
    "bnb": ("BNB", "0x1ee75a52170b17b37184d52cd7fad47551856671", "◆"),
}

# Messages
WELCOME = """🚀 **Welcome to OpenAsset Club!**

👋 I'm your AI trading bot companion!

🤖 *What I do:*
• Automated trading (8 bots)
• 24/7 market monitoring
• Risk management & alerts
• Live tracking

💡 *Philosophy:*
Remove emotion. Pure AI strategy.

📊 Choose an option below!
"""

BOTS_MSG = """🤖 **Available Trading Bots**

**Tier 1 - Professional ($9.99/mo)**
🔴 ATBOT - Alpaca (Stocks)
🔵 BTBOT - Binance (Crypto)
🟡 ETBOT - eToro (Forex)

**Tier 2 - Multi-Asset ($7.99/mo)**
🟢 BOT1 - Crypto Assets
⚪ BOT2 - Stocks
🟣 BOT3 - Commodities
🟠 BOT4 - Forex

**Tier 3 - Speed ($5.99/mo)**
🔶 BOT5 - Scalper

💬 Questions? Use /report
"""

PAYMENT_MSG = """💳 **Secure Crypto Payments**

Accept 4 crypto coins:

**Fast Options:**
₮ USDT (Tron) - Instant
◆ BNB - Quick

**Secure Options:**
₿ Bitcoin - Most secure
Ξ Ethereum - Smart chain

All verified ✅
"""

HELP_MSG = """📚 **Commands**

/start - Main menu
/bots - View bots
/payment - Pay info
/stats - Your stats
/trades - Trade history
/dashboard - Web panel
/report - Send feedback
/help - This menu
"""

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def add_user(user_id, first_name, username):
    users = load_json(DB_USERS)
    if str(user_id) not in users:
        users[str(user_id)] = {
            "first_name": first_name,
            "username": username,
            "joined": datetime.now().isoformat()
        }
        save_json(DB_USERS, users)

def add_report(user_id, username, text):
    reports = load_json(DB_REPORTS)
    report_id = f"REP_{len(reports) + 1}"
    reports[report_id] = {
        "user_id": user_id,
        "username": username,
        "message": text,
        "timestamp": datetime.now().isoformat()
    }
    save_json(DB_REPORTS, reports)
    return report_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.first_name, user.username or "user")
    
    keyboard = [
        [InlineKeyboardButton("🤖 Bots", callback_data="bots"), InlineKeyboardButton("💰 Pay", callback_data="pay")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats"), InlineKeyboardButton("📈 Dashboard", callback_data="dash")],
        [InlineKeyboardButton("💬 Chat", callback_data="chat"), InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    await update.message.reply_text(WELCOME, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(BOTS_MSG, parse_mode='Markdown')

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PAYMENT_MSG, parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 **Your Stats**\n\nReady for Phase 2! Connect accounts to see:\n✅ P&L\n✅ Win rate\n✅ Performance"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 **Recent Trades**\n\nNo trades yet. Ready for Phase 2! 🚀", parse_mode='Markdown')

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Open Dashboard", url=DASHBOARD_URL)]]
    msg = f"📈 **Dashboard**\n\nReal-time trading panel at:\n{DASHBOARD_URL}"
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MSG, parse_mode='Markdown')

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['expecting_report'] = True
    await update.message.reply_text("📝 **Send Feedback**\n\nType your message:\n• Bugs\n• Features\n• Questions", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "bots":
        await query.edit_message_text(text=BOTS_MSG, parse_mode='Markdown')
    elif data == "pay":
        kbd = [
            [InlineKeyboardButton("₿ Bitcoin", callback_data="pay_btc")],
            [InlineKeyboardButton("Ξ Ethereum", callback_data="pay_eth")],
            [InlineKeyboardButton("₮ USDT", callback_data="pay_usdt")],
            [InlineKeyboardButton("◆ BNB", callback_data="pay_bnb")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")],
        ]
        await query.edit_message_text(text=PAYMENT_MSG, reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    elif data.startswith("pay_"):
        key = data.split("_")[1]
        name, addr, sym = CRYPTOS[key]
        msg = f"💳 **{name}**\n\n`{addr}`\n\nVerified ✅"
        kbd = [[InlineKeyboardButton("⬅️ Back", callback_data="pay")]]
        await query.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    elif data == "stats":
        msg = "📊 **Stats**\n\n✅ Ready for Phase 2!"
        await query.edit_message_text(text=msg, parse_mode='Markdown')
    elif data == "dash":
        kbd = [[InlineKeyboardButton("📊 Open", url=DASHBOARD_URL)]]
        msg = f"📈 Dashboard: {DASHBOARD_URL}"
        await query.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    elif data == "chat":
        kbd = [
            [InlineKeyboardButton("📢 Channel", url="https://t.me/openassetclub")],
            [InlineKeyboardButton("📱 Group", url="https://t.me/openassetclub_updates")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")],
        ]
        msg = "💬 **Community**\n\nJoin us for discussions!"
        await query.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    elif data == "help":
        await query.edit_message_text(text=HELP_MSG, parse_mode='Markdown')
    elif data == "back":
        kbd = [
            [InlineKeyboardButton("🤖 Bots", callback_data="bots"), InlineKeyboardButton("💰 Pay", callback_data="pay")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats"), InlineKeyboardButton("📈 Dashboard", callback_data="dash")],
            [InlineKeyboardButton("💬 Chat", callback_data="chat"), InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        await query.edit_message_text(text=WELCOME, reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('expecting_report'):
        user = update.effective_user
        report_id = add_report(user.id, user.username or user.first_name, update.message.text)
        
        msg = f"✅ **Report Received!**\n\nID: `{report_id}`\n\nThank you! 💚"
        await update.message.reply_text(msg, parse_mode='Markdown')
        context.user_data['expecting_report'] = False

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bots", bots))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("trades", trades))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error)
    
    print("✅ Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
BOTEND

chmod +x /root/openasset_club/telegram_bot/main.py

echo "✅ Enhanced bot created!"
echo ""

# Start bot
cd /root/openasset_club/telegram_bot
nohup python3 main.py > /root/openasset_club/telegram_bot/logs/bot.log 2>&1 &

sleep 2

echo "✅ Bot started!"
echo ""
echo "🤖 Test the bot:"
echo "   Telegram: @openasset_club_bot"
echo "   Send: /start"
echo ""

BOTDEPLOY
```

---

## ✅ **FEATURES INCLUDED:**

```
✅ Welcome & greeting messages
✅ All commands (/start, /bots, /payment, /stats, /trades, /dashboard, /help, /report)
✅ Professional button navigation
✅ Payment system with 4 cryptos
✅ Reporting/feedback system
✅ User database tracking
✅ Report database
✅ Better UX like PALLADIUM AI
✅ Error handling
```

---

## 🎯 **AFTER DEPLOYMENT:**

Test these commands in Telegram:

```
/start        - See main menu with buttons
/bots         - View all 8 bots
/payment      - Show payment options
/stats        - Your trading stats
/trades       - Recent trades
/dashboard    - Open web dashboard
/report       - Send feedback
/help         - Show all commands
```

---

## 📝 **REPORTING SYSTEM:**

When user runs `/report`:
1. Bot asks for their message
2. User types feedback
3. Report saved to `reports.json`
4. Bot confirms with report ID
5. You can review all reports anytime

---

Let me know when you want to:
1. ✅ Deploy this bot
2. ⏳ Add more features
3. ⏳ Build Phase 2 (exchange integration)

Ready? 🚀
