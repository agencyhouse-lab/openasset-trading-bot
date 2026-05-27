# 💰 CRYPTO PAYMENT SYSTEM - SETUP GUIDE

Complete setup for per-bot crypto subscriptions!

---

## 🎯 WHAT THIS SYSTEM DOES

```
User clicks /payment
    ↓
Selects cryptocurrency (BTC, ETH, USDT, BNB)
    ↓
Gets wallet address + QR code
    ↓
Sends crypto payment
    ↓
Bot verifies payment
    ↓
User gets bot access
```

**Completely crypto-only. No credit cards, PayPal, or traditional payment.**

---

## 💳 BOT SUBSCRIPTION PRICES

Each bot is a separate subscription:

```
BTBOT (Binance)           $9.99/month
ETBOT (eToro)             $9.99/month
ATBOT (Alpaca)            $9.99/month
BOT1 (Crypto Multi)       $7.99/month
BOT2 (Stocks)             $7.99/month
BOT3 (Commodities)        $7.99/month
BOT4 (Forex)              $7.99/month
BOT5 (Scalper Crypto)     $5.99/month
```

**User can subscribe to multiple bots!**
Example: User subscribes to BTBOT + ETBOT = $19.98/month total

---

## 🪙 ACCEPTED CRYPTOCURRENCIES

### Bitcoin (BTC)
```
Monthly Cost: 0.00024 BTC (~$10)
Network: Bitcoin Mainnet
Confirmation: 10 minutes - 1 hour
Fee: User pays network fee
```

### Ethereum (ETH)
```
Monthly Cost: 0.00476 ETH (~$10)
Network: Ethereum (ERC20)
Confirmation: 15-30 seconds
Fee: User pays gas fee
```

### USDT (Tether)
```
Monthly Cost: $10 USDT (exactly)
Networks: Ethereum (ERC20) / Polygon / BSC
Confirmation: Instant to 1 minute (depends on network)
Fee: Minimal or none (Polygon is cheapest)
```

### Binance Coin (BNB)
```
Monthly Cost: 0.0167 BNB (~$10)
Network: Binance Smart Chain (BEP20)
Confirmation: 10-15 seconds
Fee: Very low (~$0.05)
```

---

## 🔐 STEP 1: Create Crypto Wallets

You need **at least ONE wallet** for each cryptocurrency.

### Option A: Use Existing Wallet (EASIEST)

If you already have wallets, just use those!

Examples:
- MetaMask (Ethereum, USDT, BNB)
- Trust Wallet (All cryptocurrencies)
- Hardware Wallet (Most secure)
- Exchange Wallet (Coinbase, Kraken, etc.)

**Get the address and add to bot config.**

### Option B: Create New Wallets

```
For Bitcoin:
1. Go to blockchain.com
2. Create account
3. Get receive address
4. Copy address to config

For Ethereum/USDT/BNB:
1. Go to metamask.io
2. Create wallet
3. Write down seed phrase (BACKUP!)
4. Get receive address
5. Copy to config
```

---

## ⚙️ STEP 2: Update Bot Configuration

Edit `/root/telegram_bot_crypto_payments.py`:

Find this section:
```python
CRYPTO_WALLETS = {
    "Bitcoin": {
        "address": "1A1z7agoat2YrQQ98XWwxvVHUYkpqB",  # ← YOUR BTC ADDRESS
        ...
    },
    "Ethereum": {
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f5dD8b",  # ← YOUR ETH ADDRESS
        ...
    },
    ...
}
```

**Replace wallet addresses with YOUR ACTUAL ADDRESSES!**

Example:
```python
CRYPTO_WALLETS = {
    "Bitcoin": {
        "address": "13aL2HzT4bhcVJFWRdnCrK7DRkBcVJfJsQ",  # YOUR BTC WALLET
        "network": "Bitcoin Mainnet",
        "symbol": "BTC",
        "price_usd": 42500,
        "monthly_cost_btc": 0.00024,
        "icon": "₿"
    },
    "Ethereum": {
        "address": "0x1234567890abcdef1234567890abcdef12345678",  # YOUR ETH WALLET
        "network": "Ethereum (ERC20)",
        "symbol": "ETH",
        "price_usd": 2100,
        "monthly_cost_eth": 0.00476,
        "icon": "Ξ"
    },
    "USDT": {
        "address": "0x1234567890abcdef1234567890abcdef12345678",  # SAME AS ETH
        "network": "Ethereum (ERC20) / Polygon / BSC",
        "symbol": "USDT",
        "price_usd": 1,
        "monthly_cost_usdt": 10,
        "icon": "₮"
    },
    "Binance Coin": {
        "address": "0x1234567890abcdef1234567890abcdef12345678",  # BSC WALLET
        "network": "Binance Smart Chain (BEP20)",
        "symbol": "BNB",
        "price_usd": 600,
        "monthly_cost_bnb": 0.0167,
        "icon": "◆"
    }
}
```

**Save the file!**

---

## 📋 STEP 3: Configure Bot Prices

The bot prices are already set:

```python
BOT_PRICES = {
    "BTBOT": {
        "name": "Binance Live Trading",
        "price": 9.99,  # ← Change if you want
        ...
    },
    "ETBOT": {
        "price": 9.99,
        ...
    },
    ...
}
```

You can adjust prices, but remember to update crypto costs too!

---

## 🚀 STEP 4: Deploy Bot

```bash
# Copy bot file to VPS
scp telegram_bot_crypto_payments.py root@maxhive.cloud:/root/

# SSH into VPS
ssh root@maxhive.cloud

# Update .env (if needed)
nano /root/.env
# Add or update:
TELEGRAM_BOT_TOKEN=YOUR_TOKEN

# Run bot
python3 /root/telegram_bot_crypto_payments.py

# Should show:
# ✅ Bot started!
# Commands:
#   /start   - Main menu
#   /payment - Crypto payment options
#   /guide   - User guide
```

---

## 📱 STEP 5: Test in Telegram

### Test /start
```
Send: /start

Expected: Main menu with [🤖 View Bots] [💰 Payment] etc.
```

### Test /payment
```
Send: /payment

Expected: Crypto selection
[₿ Bitcoin] [Ξ Ethereum] [₮ USDT] [◆ Binance Coin]
```

### Test wallet display
```
Click: [₿ Bitcoin]

Expected: Wallet address + QR code
Shows: 
- Your Bitcoin address
- "Send X BTC to this address"
- QR code image
```

### Test /guide
```
Send: /guide

Expected: Full user guide showing:
- What is the bot?
- How to get started
- Available bots
- Payment options
- FAQ
```

**Everything working? Great! Ready to launch!** ✅

---

## 💸 PAYMENT VERIFICATION FLOW

Currently, the bot:
1. Shows wallet address
2. User sends crypto
3. Bot waits for manual confirmation

### To Auto-Verify Payments:

You'd need to monitor blockchain for payments. This requires:

Option 1: Use Blockchain API
```python
# Check for incoming payments
from bitcoinlib.services import bitcoind_service

def check_bitcoin_payment(address, amount_btc):
    # Check blockchain for payment
    # If found, activate user
    pass
```

Option 2: Use Webhook
```
Set up webhook on blockchain.com
When payment received to wallet → Notify bot
Bot auto-activates subscription
```

Option 3: Manual Verification (For MVP)
```
1. User sends crypto
2. User sends transaction hash via /confirm
3. You verify manually
4. You activate manually
```

**For MVP, Option 3 is simplest!**

---

## 📊 PAYMENT TRACKING

Bot automatically tracks:
- User ID
- Bot subscribed to
- Subscription expiry date
- Payment history

Access via:
```python
user = get_user(user_id)
user.subscriptions  # {bot_name: expiry_date}
user.payments       # List of payments
user.get_active_bots()  # Active subscriptions
```

---

## 🔐 SECURITY BEST PRACTICES

```
✅ DO:
├ Use hardware wallet (most secure)
├ Enable 2FA on wallet account
├ Backup seed phrase (offline!)
├ Use separate wallet for this bot
├ Verify wallet address multiple times
└ Monitor wallet for incoming payments

❌ DON'T:
├ Share private keys
├ Store seed phrase in plain text
├ Use same wallet for other purposes
├ Accept unverified payments
├ Trust user screenshots
└ Manually transfer funds before verification
```

---

## 💰 RECOMMENDED SETUP

```
Option 1: Hardware Wallet (MOST SECURE)
├ Ledger Nano S/X (costs ~$50-100)
├ Holds all crypto safely
├ Get receive addresses for each coin
└ Store offline except for payments

Option 2: MetaMask (EASY FOR ERC20)
├ Free browser wallet
├ Good for Ethereum/USDT/BNB
├ Can use multiple accounts
├ Accept Bitcoin separately

Option 3: Exchange Wallet (CONVENIENT)
├ Coinbase, Kraken, Binance
├ Built-in security
├ Easy to convert to cash
└ Lower fees
```

**Recommended for you: Option 2 (MetaMask for ERC20) + Option 1 (Hardware for BTC)**

---

## 📈 FINANCIAL PROJECTION

### Monthly Pricing Example

```
BTBOT: $9.99/month
100 users × $9.99 = $999/month

BTBOT + ETBOT: $19.98/month
50 users × $19.98 = $999/month

5 bots × 100 users = 500 subscriptions
500 × $9.99 = $4,995/month revenue!
```

### Example: 1000 Subscription Total

```
1000 subscriptions × $8.50 average = $8,500/month
= $102,000/year

Costs:
- VPS: $20/month
- Crypto gas fees: ~5% of transactions

Net: ~$95,000/year ✅
```

---

## 🆘 TROUBLESHOOTING

### QR Code Not Showing?

```bash
# Install qrcode library
pip install qrcode pillow

# Restart bot
python3 /root/telegram_bot_crypto_payments.py
```

### Wallet Address Error?

1. Check address is correct (copy/paste)
2. Verify address is on correct network
3. Make sure it's a RECEIVE address, not exchange address

### User Says They Sent Payment?

1. Ask for transaction hash
2. Check blockchain explorer:
   - Bitcoin: blockchain.com
   - Ethereum: etherscan.io
   - Binance: bscscan.com
3. Verify payment amount matches
4. Activate subscription manually when confirmed

---

## 🎯 LAUNCHING

Before launching to public:

```
✅ Wallets created
✅ Wallet addresses in bot config
✅ Bot tested locally
✅ All commands working
✅ QR codes generating
✅ User guide complete
✅ Prices finalized

Then:
1. Deploy to VPS
2. Invite 5 beta testers
3. Have them send test payments
4. Verify payments work
5. Launch to public
```

---

## 📱 USER EXPERIENCE

### User's Payment Journey:

```
User: /start
Bot: [💰 Payment]

User: [💰 Payment]
Bot: [₿ Bitcoin] [Ξ Ethereum] [₮ USDT] [◆ BNB]

User: [₮ USDT]
Bot: Shows wallet address + QR code
Bot: "Send $10 USDT to this address"
Bot: "Monthly cost for any bot"

User: Opens wallet app (MetaMask, Trust Wallet, etc.)
User: Scans QR code
User: Sends $10 USDT
User: Confirms transaction

Bot: Waits for confirmation (5-30 seconds)
Bot: Receives payment notification
Bot: Automatically activates subscription
Bot: Sends: "✅ Payment confirmed! BTBOT is now active!"

User: Can now /dashboard and see trades
```

---

## 🚀 YOU'RE READY!

Next steps:

1. Get your wallet addresses
2. Update bot config
3. Deploy to VPS
4. Test with beta users
5. Launch to public

**Pure crypto payments. No middlemen. All funds go to you directly!** 💰

Good luck! 🚀
