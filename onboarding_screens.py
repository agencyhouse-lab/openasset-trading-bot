#!/usr/bin/env python3
"""
OpenAsset User Onboarding & Education Hub
==========================================

Two user types:
1. Non-Traders → AI auto-trades for you (hands-off, passive income)
2. Experienced Traders → AI tips & signals to amplify profits (active, strategic)

Educational content:
- How to start (setup, connection, first trade)
- How to profit (signal interpretation, risk management)
- How to withdraw (secure, tax-aware, timing)
"""

# Onboarding screens for trading_dashboard.py

def screen_onboarding_type():
    """Choose user type: non-trader vs experienced trader."""
    text = (
        "👋 *Welcome to OpenAsset Trading Bot!*\n\n"
        "What's your trading background?\n\n"
        "🟢 *I don't trade — AI trades for me*\n"
        "├ No experience needed\n"
        "├ AI auto-executes signals 24/7\n"
        "├ Hands-off passive income\n"
        "└ Risk-managed ($50/trade, 0.5% SL)\n\n"
        "🔵 *I know trading — I need tips*\n"
        "├ Experienced trader\n"
        "├ AI gives signals + market tips\n"
        "├ You decide when to act\n"
        "└ Amplify profits with strategy"
    )
    return text, kb(
        [("🟢 Auto-Trade (Hands-Off)", "onboard_autotrade")],
        [("🔵 Tips + Signals (Hands-On)", "onboard_manual")],
        [("❓ Learn More", "onboard_learn")],
    )


def screen_onboarding_autotrade():
    """Onboarding for non-traders (AI auto-trading)."""
    text = (
        "🤖 *Auto-Trading Mode (Perfect for You!)*\n\n"
        "AI trades 24/7. You just watch profits grow.\n\n"
        "*How it works:*\n"
        "1. Connect account (Binance/Alpaca/OANDA)\n"
        "2. Enable AI Signals\n"
        "3. Set initial balance\n"
        "4. AI auto-trades with SL/TP\n"
        "5. Watch dashboard for P&L\n\n"
        "*No decisions needed — AI handles everything.*\n\n"
        "Max $50 per trade, 0.5% stop-loss = safety first."
    )
    return text, kb(
        [("📱 How to Connect", "guide_connect_binance")],
        [("⚙️ Enable AI Signals", "guide_enable_signals")],
        [("💰 First $50 Trade", "guide_first_trade")],
        [("📊 Watch Dashboard", "guide_dashboard")],
        [("⬅️ Back", "td_home")],
    )


def screen_onboarding_manual():
    """Onboarding for experienced traders (tips mode)."""
    text = (
        "📈 *Trader's Mode (For Pros)*\n\n"
        "AI gives signals. You execute strategically.\n\n"
        "*How it works:*\n"
        "1. AI calculates: RSI + MACD + Bollinger Bands\n"
        "2. Sends you signal: BUY / SELL / HOLD\n"
        "3. You decide trade size & entry\n"
        "4. Manual execution on your terms\n"
        "5. AI tracks your P&L\n\n"
        "*Why this works:*\n"
        "├ Avoid FOMO trades (AI validates first)\n"
        "├ Size positions to YOUR risk tolerance\n"
        "├ Use signals as bias confirmation\n"
        "└ Amplify wins, minimize losses"
    )
    return text, kb(
        [("📊 Understand Signals", "guide_signals_explained")],
        [("💡 Trading Tips", "guide_trading_tips")],
        [("🎯 Risk Management", "guide_risk_mgmt")],
        [("📈 Profit Tracking", "guide_profit_track")],
        [("⬅️ Back", "td_home")],
    )


def screen_guide_connect_binance():
    """How to connect Binance."""
    text = (
        "🔗 *Connect Binance (5 Minutes)*\n\n"
        "Step 1: Create Binance API Key\n"
        "├ Go to binance.com\n"
        "├ Account → API Management\n"
        "├ Create New Key (label: 'OpenAsset Bot')\n"
        "└ COPY your Key & Secret\n\n"
        "Step 2: Enable Permissions\n"
        "├ ☑️ Enable Spot & Margin Trading\n"
        "├ ☑️ Enable Reading\n"
        "└ IP Whitelist: 72.62.254.237\n\n"
        "Step 3: Paste in Bot\n"
        "├ /trading → Trading Menu → Binance\n"
        "├ Paste API Key\n"
        "├ Paste Secret Key\n"
        "└ ✅ Verified!"
    )
    return text, kb(
        [("⚠️ Safety Tips", "guide_api_safety")],
        [("✅ Next: Enable AI", "guide_enable_signals")],
        [("⬅️ Back", "onboard_autotrade")],
    )


def screen_guide_enable_signals():
    """How to enable AI signals."""
    text = (
        "🤖 *Enable AI Auto-Trading (2 Steps)*\n\n"
        "Step 1: Turn On AI Signals\n"
        "├ /trading\n"
        "├ Settings ⚙️\n"
        "├ AI Signals 🤖\n"
        "└ ✅ Toggle ON\n\n"
        "Step 2: Choose Platform\n"
        "├ Settings → AI Signals → Change Mode\n"
        "├ Pick: 🔶 Binance (crypto)\n"
        "│       📊 Alpaca (stocks)\n"
        "│       💱 OANDA (forex)\n"
        "│       🏛 Strategy Lab (practice)\n"
        "└ ✅ Ready!\n\n"
        "AI now checks signals every 60 minutes.\n"
        "First trade in ~1 hour!"
    )
    return text, kb(
        [("💰 First Trade Details", "guide_first_trade")],
        [("📊 Watch Dashboard", "guide_dashboard")],
        [("⬅️ Back", "onboard_autotrade")],
    )


def screen_guide_first_trade():
    """Explain first trade."""
    text = (
        "🎯 *Your First $50 AI Trade*\n\n"
        "*What happens:*\n"
        "AI generates signal:\n"
        "  BTC price: $69,705\n"
        "  RSI: 28 (oversold)\n"
        "  MACD: Golden cross\n"
        "  BB: Near lower band\n"
        "  → 3 indicators agree = BUY\n\n"
        "*Execution:*\n"
        "  Order: $50 BTC/USDT\n"
        "  Stop-loss: $69,352 (-0.5%)\n"
        "  Take-profit: $71,794 (+3.0%)\n"
        "  Auto-close when hit\n\n"
        "*Your P&L:*\n"
        "  Best case: +$1.50 (3% win)\n"
        "  Worst case: -$0.25 (0.5% loss)\n"
        "  Risk/Reward: 1:6 ✅"
    )
    return text, kb(
        [("📊 Dashboard", "guide_dashboard")],
        [("💡 Trading Tips", "guide_trading_tips")],
        [("⬅️ Back", "onboard_autotrade")],
    )


def screen_guide_dashboard():
    """How to use dashboard."""
    text = (
        "📊 *Your Trading Dashboard*\n\n"
        "/trading → My Portfolio\n\n"
        "Shows:\n"
        "├ 💰 Total Balance: $10,000\n"
        "├ 📈 Open Positions: 3\n"
        "│   ├ BTC: +2.5% (winning)\n"
        "│   ├ SPY: -0.3% (slight loss)\n"
        "│   └ EUR: +1.1%\n"
        "├ 📊 Win Rate: 62%\n"
        "├ 💵 Total P&L: +$350\n"
        "└ 📉 Max Daily Loss: -$50\n\n"
        "/trading → Statistics\n"
        "├ Monthly ROI: 8.5%\n"
        "├ Best Trade: +$4.20\n"
        "├ Worst Trade: -$1.80\n"
        "└ Average Win/Loss: $1.50/$0.40"
    )
    return text, kb(
        [("💵 Withdraw Profit", "guide_withdraw")],
        [("⬅️ Back", "onboard_autotrade")],
    )


def screen_guide_api_safety():
    """API key safety tips."""
    text = (
        "🔐 *API Key Safety*\n\n"
        "✅ DO:\n"
        "├ Create separate API key just for bot\n"
        "├ Label it: 'OpenAsset Bot'\n"
        "├ Enable ONLY: Spot Trading + Reading\n"
        "├ IP Whitelist: 72.62.254.237\n"
        "├ Rotate keys monthly\n"
        "└ Use read-only key for testing\n\n"
        "❌ DON'T:\n"
        "├ Share key with anyone\n"
        "├ Enable withdrawals\n"
        "├ Enable margin/leverage\n"
        "├ Use your main account key\n"
        "└ Disable IP whitelist\n\n"
        "💡 Best practice: Use $100-$500 only."
    )
    return text, kb(
        [("⬅️ Back", "guide_connect_binance")],
    )


def screen_guide_signals_explained():
    """Explain signals for traders."""
    text = (
        "📊 *Understanding AI Signals*\n\n"
        "Three indicators work together:\n\n"
        "1️⃣ *RSI (Momentum)*\n"
        "   < 30 = Oversold = BUY bias\n"
        "   > 70 = Overbought = SELL bias\n\n"
        "2️⃣ *MACD (Trend)*\n"
        "   Line crosses above signal = BUY\n"
        "   Line crosses below signal = SELL\n\n"
        "3️⃣ *Bollinger Bands (Volatility)*\n"
        "   Price at lower band = BUY\n"
        "   Price at upper band = SELL\n\n"
        "🎯 *Signal = 2+ indicators agree*\n"
        "   Reduces false signals by 60%"
    )
    return text, kb(
        [("💡 Use This Signal", "guide_signal_usage")],
        [("⬅️ Back", "onboard_manual")],
    )


def screen_guide_trading_tips():
    """Trading tips for experienced traders."""
    text = (
        "💡 *Pro Trading Tips*\n\n"
        "1️⃣ *Wait for Confirmation*\n"
        "   Don't trade on first signal\n"
        "   Wait for 2-3 same signals\n"
        "   = Higher win rate\n\n"
        "2️⃣ *Size Your Positions*\n"
        "   Use AI signal as bias only\n"
        "   Size based on your risk:\n"
        "   └ 1% rule: Risk 1% per trade\n\n"
        "3️⃣ *Manage Your Emotions*\n"
        "   ✅ Take profits at TP\n"
        "   ✅ Cut losses at SL\n"
        "   ❌ Don't hold winning trades\n"
        "   ❌ Don't revenge trade\n\n"
        "4️⃣ *Track Everything*\n"
        "   Win rate, avg win/loss, ROI\n"
        "   This builds repeatable edge"
    )
    return text, kb(
        [("🎯 Risk Management", "guide_risk_mgmt")],
        [("⬅️ Back", "onboard_manual")],
    )


def screen_guide_risk_mgmt():
    """Risk management guide."""
    text = (
        "🛡️ *Risk Management Framework*\n\n"
        "Position Sizing:\n"
        "├ 1% Rule: Risk 1% account per trade\n"
        "│  $10k account → max $100 risk\n"
        "├ Max 3 concurrent positions\n"
        "└ Daily loss limit: -$500\n\n"
        "Entry Rules:\n"
        "├ Wait for signal confirmation\n"
        "├ Avoid trading before news\n"
        "├ Trade only market hours\n"
        "└ Skip choppy sideways markets\n\n"
        "Exit Rules:\n"
        "├ Always set SL (0.5% minimum)\n"
        "├ Always set TP (3% minimum)\n"
        "├ Take profits at TP\n"
        "└ Cut losses at SL (no exceptions!)\n\n"
        "Goal: Win 60% of trades\n"
        "Result: 6 wins × $1.50 = $9 profit\n"
        "        4 losses × -$0.25 = -$1 loss\n"
        "        Net: +$8 on $500 = 1.6% ROI"
    )
    return text, kb(
        [("💰 Profit Tracking", "guide_profit_track")],
        [("⬅️ Back", "onboard_manual")],
    )


def screen_guide_withdraw():
    """How to safely withdraw profits."""
    text = (
        "💵 *Withdraw Profits Safely*\n\n"
        "✅ Best Practice:\n"
        "├ Wait 24-48 hours after trade closes\n"
        "├ Withdraw 50% of profits monthly\n"
        "├ Keep 50% for next month's trading\n"
        "├ Use main bank, not intermediary\n"
        "└ Track for tax reporting\n\n"
        "Steps (Binance example):\n"
        "1. Wallet → Spot Wallet\n"
        "2. Select USDT\n"
        "3. Withdraw → Bank (ACH)\n"
        "4. Enter amount\n"
        "5. Confirm (takes 1-3 days)\n\n"
        "*Tax Note:*\n"
        "Report all trades to accountant\n"
        "Keep: date, symbol, entry, exit, P&L"
    )
    return text, kb(
        [("📊 Track Dashboard", "guide_dashboard")],
        [("⬅️ Back", "onboard_autotrade")],
    )


def screen_guide_learn():
    """Educational resources."""
    text = (
        "📚 *Learn Trading*\n\n"
        "*Free Resources:*\n"
        "├ TradingView: Technical analysis\n"
        "├ Investopedia: Beginner courses\n"
        "├ YouTube: 'RSI Trading' tutorial\n"
        "└ Books: 'Market Wizards' (interview)\n\n"
        "*Our Bot Teaches:*\n"
        "├ Real money = Real learning\n"
        "├ SL/TP discipline = Win rate\n"
        "├ Position sizing = Survival\n"
        "└ Emotion control = Consistency\n\n"
        "*Your First Month:*\n"
        "├ Make 20-30 trades\n"
        "├ Track every signal\n"
        "├ Learn from losses\n"
        "└ Optimize strategy\n\n"
        "After 1 month: You'll be a trader ✅"
    )
    return text, kb(
        [("🔵 Tips Mode", "onboard_manual")],
        [("🟢 Auto Trade Mode", "onboard_autotrade")],
        [("⬅️ Back", "td_home")],
    )


# OANDA Connection Guide

def screen_guide_connect_oanda():
    """How to connect OANDA."""
    text = (
        "💱 *Connect OANDA Forex (10 Minutes)*\n\n"
        "Step 1: Create OANDA Account\n"
        "├ Visit oanda.com\n"
        "├ Sign up (free practice account)\n"
        "├ Or upgrade to live account\n"
        "└ Verify email\n\n"
        "Step 2: Generate API Token\n"
        "├ Account Settings → API\n"
        "├ Generate Personal Access Token\n"
        "├ Copy token (shown once!)\n"
        "└ Account ID: 001-001-XXXXXX-001\n\n"
        "Step 3: Connect in Bot\n"
        "├ /trading → Trading Menu → OANDA\n"
        "├ Paste API Token\n"
        "├ Paste Account ID\n"
        "└ ✅ Connected!\n\n"
        "*Instruments Available:*\n"
        "EUR/USD, GBP/USD, Gold, Oil, Indices"
    )
    return text, kb(
        [("🔐 API Safety", "guide_api_safety")],
        [("📈 Start Trading", "guide_first_trade")],
        [("⬅️ Back", "guide_enable_signals")],
    )
