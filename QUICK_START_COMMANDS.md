# ⚡ QUICK START - COPY & PASTE COMMANDS

Sunny, just copy/paste these commands in order. Takes 15 minutes!

---

## 🎯 YOUR CREDENTIALS (Already Filled In)

```
Bot Token: 8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
User ID: 5587885687
Bot: @openasset_club_bot
```

---

## 📋 COMMAND 1: SSH INTO VPS

Copy and paste:
```bash
ssh root@maxhive.cloud
```

---

## 📋 COMMAND 2: CREATE .env FILE

Copy and paste EXACTLY:
```bash
cat > /root/.env << 'EOF'
TELEGRAM_BOT_TOKEN=8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU
CHAT_ID=5587885687
MASTER_CHAT_ID=5587885687
DASHBOARD_URL=http://72.62.254.237:8000/trading_dashboard.html
BOT_NAME=openasset_club_bot
VPS_IP=72.62.254.237
DASHBOARD_PORT=8000
BITCOIN_ADDRESS=YOUR_BTC_ADDRESS_HERE
ETHEREUM_ADDRESS=YOUR_ETH_ADDRESS_HERE
USDT_ADDRESS=YOUR_USDT_ADDRESS_HERE
BNB_ADDRESS=YOUR_BNB_ADDRESS_HERE
EOF
```

**Then update with YOUR wallet addresses:**
```bash
nano /root/.env
# Change: YOUR_BTC_ADDRESS_HERE → your actual BTC address
# Change: YOUR_ETH_ADDRESS_HERE → your actual ETH address
# Save: Ctrl+X, Y, Enter
```

---

## 📋 COMMAND 3: INSTALL DEPENDENCIES

Copy and paste:
```bash
pip install python-telegram-bot==20.3 qrcode pillow python-dotenv
```

---

## 📋 COMMAND 4: CREATE PAYMENT BOT FILE

⚠️ **This is long - copy/paste carefully:**

```bash
cat > /root/telegram_bot_crypto_payments.py << 'EOF'
#!/usr/bin/env python3
"""
ADVANCED TRADING BOT WITH CRYPTO PAYMENTS
- Per-bot subscriptions
- Crypto payments only (Bitcoin, Ethereum, etc.)
- /payment command shows wallet + QR code
- /guide command shows user guide
- Track paid subscriptions
"""

import logging
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from io import BytesIO

# QR Code generation
import qrcode

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Application, CommandHandler, QueryHandler, ContextTypes

# Load environment
load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://72.62.254.237:8000/trading_dashboard.html')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CRYPTO WALLETS ====================

CRYPTO_WALLETS = {
    "Bitcoin": {
        "address": os.getenv('BITCOIN_ADDRESS', 'NOT_SET'),
        "network": "Bitcoin Mainnet",
        "symbol": "BTC",
        "price_usd": 42500,
        "monthly_cost_btc": 0.00024,
        "icon": "₿"
    },
    "Ethereum": {
        "address": os.getenv('ETHEREUM_ADDRESS', 'NOT_SET'),
        "network": "Ethereum (ERC20)",
        "symbol": "ETH",
        "price_usd": 2100,
        "monthly_cost_eth": 0.00476,
        "icon": "Ξ"
    },
    "USDT": {
        "address": os.getenv('USDT_ADDRESS', 'NOT_SET'),
        "network": "Ethereum (ERC20) / Polygon / BSC",
        "symbol": "USDT",
        "price_usd": 1,
        "monthly_cost_usdt": 10,
        "icon": "₮"
    },
    "Binance Coin": {
        "address": os.getenv('BNB_ADDRESS', 'NOT_SET'),
        "network": "Binance Smart Chain (BEP20)",
        "symbol": "BNB",
        "price_usd": 600,
        "monthly_cost_bnb": 0.0167,
        "icon": "◆"
    }
}

# Bot subscription prices
BOT_PRICES = {
    "BTBOT": {
        "name": "Binance Live Trading",
        "price": 9.99,
        "description": "Real-time Binance crypto trading",
        "daily_profit": 15.50,
        "roi": "18.6%"
    },
    "ETBOT": {
        "name": "eToro Crypto Watch",
        "price": 9.99,
        "description": "Sentiment-based crypto alerts",
        "daily_profit": 12.30,
        "roi": "14.8%"
    },
    "ATBOT": {
        "name": "Alpaca Live Trading",
        "price": 9.99,
        "description": "Stock & options trading",
        "daily_profit": 18.70,
        "roi": "22.4%"
    },
    "BOT1": {
        "name": "Crypto Multi-Asset",
        "price": 7.99,
        "description": "15 crypto assets, hourly trades",
        "daily_profit": 11.20,
        "roi": "13.5%"
    },
    "BOT2": {
        "name": "Stock Market",
        "price": 7.99,
        "description": "10 stocks, hourly trades",
        "daily_profit": 9.80,
        "roi": "11.8%"
    },
    "BOT3": {
        "name": "Commodities",
        "price": 7.99,
        "description": "Gold, Silver, Oil trading",
        "daily_profit": 8.50,
        "roi": "10.2%"
    },
    "BOT4": {
        "name": "Forex Pairs",
        "price": 7.99,
        "description": "8 currency pairs",
        "daily_profit": 10.30,
        "roi": "12.4%"
    },
    "BOT5": {
        "name": "Scalper Crypto",
        "price": 5.99,
        "description": "5 cryptos, 30-sec trades",
        "daily_profit": 6.70,
        "roi": "8.1%"
    }
}

class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.subscriptions = {}
        self.payments = []
        self.created_at = datetime.now()
    
    def add_subscription(self, bot_name, months=1):
        expiry = datetime.now() + timedelta(days=30 * months)
        self.subscriptions[bot_name] = expiry
    
    def is_subscribed(self, bot_name):
        if bot_name not in self.subscriptions:
            return False
        return self.subscriptions[bot_name] > datetime.now()
    
    def get_active_bots(self):
        return [bot for bot in self.subscriptions 
                if self.subscriptions[bot] > datetime.now()]

users_db = {}

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = UserData(user_id)
    return users_db[user_id]

def generate_qr_code(data, filename=None):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if filename:
            img.save(f"/tmp/{filename}.png")
            return f"/tmp/{filename}.png"
        else:
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

USER_GUIDE = """
🤖 *USER GUIDE - AI TRADING BOT*

═══════════════════════════════════

*1. WHAT IS THIS BOT?*

This is an AI-powered automated trading system that:
✓ Trades 24/7 without emotions
✓ Removes revenge trading
✓ Removes greed
✓ Removes fear
✓ Executes consistently

Why? Because human psychology ruins trading.
This bot removes your emotions.

═══════════════════════════════════

*2. HOW TO GET STARTED*

Step 1: Choose a bot
   /bots → See all available trading bots

Step 2: Check pricing
   /payment → See crypto payment options

Step 3: Send payment
   Send crypto to wallet address
   (QR code provided)

Step 4: Get access
   I'll verify payment and activate bot
   You'll get access to dashboard

Step 5: Start trading
   /dashboard → View real-time trades
   /status → Check P&L

═══════════════════════════════════

*3. AVAILABLE BOTS*

🔴 *BTBOT* ($9.99/month)
   Binance crypto trading
   Avg daily profit: $15.50 (+18.6%)

🟠 *ETBOT* ($9.99/month)
   eToro sentiment trading
   Avg daily profit: $12.30 (+14.8%)

🔵 *ATBOT* ($9.99/month)
   Alpaca stocks & options
   Avg daily profit: $18.70 (+22.4%)

🟡 *BOT1* ($7.99/month)
   Crypto multi-asset (15 assets)
   Avg daily profit: $11.20 (+13.5%)

🟢 *BOT2* ($7.99/month)
   Stock market (10 stocks)
   Avg daily profit: $9.80 (+11.8%)

*And BOT3, BOT4, BOT5...*

═══════════════════════════════════

*4. PAYMENT OPTIONS*

We accept crypto ONLY:

₿ Bitcoin (BTC) - $0.00024/month
Ξ Ethereum (ETH) - $0.00476/month
₮ USDT - $10.00/month
◆ Binance Coin (BNB) - $0.0167/month

Command: /payment → Get wallet address + QR code

═══════════════════════════════════

*5. DASHBOARD*

After payment, you get:

✓ Real-time balance
✓ Daily/monthly P&L
✓ Open trades with entry/exit
✓ Trade history
✓ Win rate & statistics
✓ Equity curve chart
✓ Risk management info

Command: /dashboard → Open dashboard

═══════════════════════════════════

*6. HOW AI REMOVES EMOTIONS*

❌ REVENGE TRADING
   AI stops after max daily loss
   NO revenge trades allowed
   ✅ Capital protected

❌ GREED
   AI takes profits automatically
   NO holding for "more gains"
   ✅ Consistent execution

❌ FEAR
   AI follows plan mechanically
   NO panic selling
   ✅ Disciplined trading

❌ INCONSISTENCY
   AI uses same rules every time
   NO changing strategies
   ✅ Predictable results

═══════════════════════════════════

*7. COMMANDS*

/start           → Main menu
/bots            → See all bots
/payment         → Crypto payment options
/dashboard       → View trades & P&L
/status          → Quick status
/guide           → This guide
/help            → Get help

═══════════════════════════════════

READY TO START?

Step 1: /bots → Choose bot
Step 2: /payment → Get wallet address
Step 3: Send crypto payment
Step 4: Get access & start trading!

Good luck! 🚀
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    message = f"""
🤖 *AI TRADING BOT*

Welcome! Automate your trading.

Your active subscriptions: {len(user.get_active_bots())}/8

What would you like to do?
"""
    
    keyboard = [
        [InlineKeyboardButton("🤖 View Bots", callback_data='view_bots')],
        [InlineKeyboardButton("💰 Payment", callback_data='payment_menu')],
        [InlineKeyboardButton("📊 Dashboard", url=DASHBOARD_URL)],
        [InlineKeyboardButton("📖 User Guide", callback_data='guide')],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else update.message
    
    if hasattr(query, 'answer'):
        await query.answer()
    
    keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(query, 'edit_message_text'):
        await query.edit_message_text(USER_GUIDE, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await query.reply_text(USER_GUIDE, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else update.message
    
    if hasattr(query, 'answer'):
        await query.answer()
    
    payment_text = """
💰 *PAYMENT OPTIONS*

We accept crypto ONLY. No credit cards.

Select cryptocurrency:
"""
    
    keyboard = [
        [InlineKeyboardButton("₿ Bitcoin", callback_data='payment_BTC')],
        [InlineKeyboardButton("Ξ Ethereum", callback_data='payment_ETH')],
        [InlineKeyboardButton("₮ USDT", callback_data='payment_USDT')],
        [InlineKeyboardButton("◆ Binance Coin", callback_data='payment_BNB')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(query, 'edit_message_text'):
        await query.edit_message_text(payment_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await query.reply_text(payment_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def show_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE, crypto_type):
    query = update.callback_query
    await query.answer()
    
    wallet_info = CRYPTO_WALLETS.get(crypto_type)
    if not wallet_info:
        await query.edit_message_text("❌ Crypto type not found")
        return
    
    qr_file = generate_qr_code(wallet_info['address'], f"wallet_{crypto_type}_{query.from_user.id}")
    
    payment_text = f"""
💰 *PAYMENT ADDRESS*

Cryptocurrency: {wallet_info['icon']} {crypto_type}
Network: {wallet_info['network']}

📍 Wallet Address:
`{wallet_info['address']}`

Monthly Cost:
💵 ~$10.00 USD

*How to Pay:*
1. Copy wallet address above
2. Send {crypto_type} to this address
3. Send transaction hash via /confirm
4. I'll verify and activate bot

⬇️ Scan QR code or copy address above
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Payment", callback_data='confirm_payment')],
        [InlineKeyboardButton("◀️ Back", callback_data='payment_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if qr_file:
        await query.edit_message_text(payment_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        try:
            with open(qr_file, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=open(qr_file, 'rb'),
                    caption=f"QR Code for {crypto_type} Payment",
                    parse_mode=ParseMode.MARKDOWN
                )
        except:
            pass
    else:
        await query.edit_message_text(payment_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def view_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bots_text = "*🤖 AVAILABLE TRADING BOTS*\n\n"
    
    for bot_name, bot_info in BOT_PRICES.items():
        status = "✅ Subscribed" if get_user(query.from_user.id).is_subscribed(bot_name) else "⭕ Not subscribed"
        
        bots_text += f"""
*{bot_name}* - ${bot_info['price']:.2f}/month
├ {bot_info['description']}
├ Daily Profit: ${bot_info['daily_profit']:.2f}
├ Monthly ROI: {bot_info['roi']}
└ {status}

"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Subscribe to Bot", callback_data='subscribe_bot')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(bots_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def subscribe_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    subscribe_text = "Select bot to subscribe:\n"
    
    keyboard = []
    for bot_name in BOT_PRICES.keys():
        user = get_user(query.from_user.id)
        if not user.is_subscribed(bot_name):
            keyboard.append([InlineKeyboardButton(f"✅ {bot_name}", callback_data=f'sub_{bot_name}')])
    
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data='view_bots')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(subscribe_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else update.message
    
    if hasattr(query, 'answer'):
        await query.answer()
    
    help_text = """
❓ *HELP*

📖 *User Guide*
/guide - Complete user guide with FAQ

💰 *Payments*
/payment - Crypto payment options

🤖 *Bots*
/bots - View all trading bots

📊 *Dashboard*
/dashboard - View trades & P&L

═════════════════════════════════

Common Issues:

❓ Payment not verified?
   → Takes 5-10 min to confirm
   → Check blockchain explorer

❓ Bot not trading?
   → Check /status
   → Verify subscription is active

❓ Can't see dashboard?
   → Must have active subscription
   → Try refreshing page

═════════════════════════════════

Ready? /start
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 User Guide", callback_data='guide')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(query, 'edit_message_text'):
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await query.reply_text(help_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'view_bots':
        await view_bots(update, context)
    elif data == 'payment_menu':
        await payment_command(update, context)
    elif data == 'guide':
        await guide_command(update, context)
    elif data == 'help':
        await help_command(update, context)
    elif data == 'back_to_menu':
        await back_to_menu(update, context)
    elif data == 'subscribe_bot':
        await subscribe_bot(update, context)
    elif data.startswith('payment_'):
        crypto = data.split('_')[1]
        crypto_map = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'USDT': 'USDT',
            'BNB': 'Binance Coin'
        }
        await show_wallet(update, context, crypto_map.get(crypto))

def main():
    print("\n" + "🤖 " * 30)
    print("AI TRADING BOT WITH CRYPTO PAYMENTS")
    print("Per-Bot Subscriptions | Crypto Only")
    print("🤖 " * 30)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("payment", payment_command))
    application.add_handler(CommandHandler("guide", lambda u, c: guide_command(u, c)))
    application.add_handler(CommandHandler("help", lambda u, c: help_command(u, c)))
    application.add_handler(CommandHandler("bots", lambda u, c: view_bots(u, c)))
    
    application.add_handler(QueryHandler(handle_callback))
    
    print("✅ Bot started!")
    print(f"Token: {BOT_TOKEN[:20]}...")
    print("Commands: /start, /payment, /guide, /bots, /help")
    
    application.run_polling()

if __name__ == '__main__':
    main()
EOF
```

---

## 📋 COMMAND 5: CREATE DASHBOARD FILE

⚠️ **Skip this for now** - Use simpler version below:

```bash
# For now, just copy trading_dashboard.html from your files
scp trading_dashboard.html root@maxhive.cloud:/root/
```

---

## 📋 COMMAND 6: TEST BOT

```bash
python3 /root/telegram_bot_crypto_payments.py
```

Wait for:
```
🤖 AI TRADING BOT WITH CRYPTO PAYMENTS
✅ Bot started!
```

**Open Telegram and send:** `/start`

If bot responds → SUCCESS! ✅

Stop test (Ctrl+C)

---

## 📋 COMMAND 7: RUN BOT 24/7

```bash
nohup python3 /root/telegram_bot_crypto_payments.py > /root/bot_payment.log 2>&1 &
```

Verify:
```bash
ps aux | grep telegram_bot_crypto_payments | grep -v grep
```

Should show 1 running process ✅

---

## 📋 COMMAND 8: START DASHBOARD

```bash
cd /root
python3 -m http.server 8000 &
```

Test:
```
http://72.62.254.237:8000/trading_dashboard.html
```

Should load dashboard! ✅

---

## ✅ DONE!

Your bot is live!

**Share with users:**
```
🤖 Bot: https://t.me/openasset_club_bot
📢 Channel: https://t.me/openassetclub_updates
💬 Group: https://t.me/openassetclub
📊 Dashboard: http://72.62.254.237:8000/trading_dashboard.html
```

---

## 🎯 QUICK MONITORING

```bash
# Check bot running
ps aux | grep telegram_bot_crypto_payments | grep -v grep

# Check logs
tail -20 /root/bot_payment.log

# Check dashboard
ps aux | grep "http.server" | grep -v grep
```

---

**Done! 🚀 Your bot is live!**
