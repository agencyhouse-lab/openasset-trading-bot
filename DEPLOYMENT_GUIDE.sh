#!/bin/bash
# OpenAsset Trading Bot - Complete VPS Deployment Guide
# =====================================================
# Run this guide step-by-step on your Hostinger VPS
# IP: 72.62.254.237
# User: root@maxhive.cloud

echo "🚀 OpenAsset VPS Deployment Guide"
echo "=================================="
echo ""
echo "STEP 1: SSH into your VPS"
echo "Command: ssh root@72.62.254.237"
echo ""
echo "Password: (enter your password)"
echo ""
echo "=================================="
echo ""

# After SSH, run these commands:

echo "STEP 2: Go to project directory"
echo "$ cd /root/openasset-trading-bot"
echo "$ git pull origin main"
echo ""

echo "STEP 3: Install API service (if not already)"
echo "$ pip3 install fastapi uvicorn"
echo ""

echo "STEP 4: Start the public API (on port 9000)"
echo "Run in background:"
echo "$ nohup python3 api_public.py > /var/log/openasset_api.log 2>&1 &"
echo ""
echo "Or in screen:"
echo "$ screen -S api"
echo "$ python3 api_public.py"
echo "$ Ctrl+A, then D to detach"
echo ""

echo "STEP 5: Verify API is running"
echo "$ curl http://localhost:9000/api/public/stats"
echo ""
echo "You should see JSON data like:"
echo '{
  "status": "operational",
  "platform": {
    "total_users": 460,
    "total_trades_executed": 1000,
    ...
  }
}'
echo ""

echo "STEP 6: Deploy bot to VPS"
echo "$ cd /root/openasset-trading-bot"
echo "$ bash install_trading_dashboard.sh"
echo ""

echo "STEP 7: Start the trading bot"
echo "$ cd /root/openasset_club/telegram_bot"
echo "$ nohup python3 main.py > logs/user_bot.log 2>&1 &"
echo ""

echo "STEP 8: Check if everything is running"
echo "$ ps aux | grep -E 'python3|main.py|api_public'"
echo ""
echo "You should see:"
echo "  ✅ main.py (user bot)"
echo "  ✅ api_public.py (public API)"
echo ""

echo "STEP 9: Test the API from your computer"
echo "Open browser or curl:"
echo "  http://72.62.254.237:9000/api/public/stats"
echo "  http://72.62.254.237:9000/api/public/trades"
echo "  http://72.62.254.237:9000/dashboard.html"
echo ""

echo "STEP 10: Check logs"
echo "$ tail -100f /root/openasset_club/telegram_bot/logs/user_bot.log"
echo "$ tail -50f /var/log/openasset_api.log"
echo ""

echo "=================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================="
echo ""
echo "YOUR ENDPOINTS:"
echo "  📊 Stats API: http://72.62.254.237:9000/api/public/stats"
echo "  📈 Trades API: http://72.62.254.237:9000/api/public/trades"
echo "  💬 Bot: @openasset_club_bot (Telegram)"
echo ""
echo "Next: Test all 3 platforms (see TEST_PLAN.txt)"
