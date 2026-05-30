# 🌐 CPANEL SETUP GUIDE
## How to Connect Your VPS Bot to openassetclub.com Website

---

## 📋 OVERVIEW

Your setup:
- **VPS Bot**: Hostinger at `72.62.254.237` (runs trading bot)
- **Website**: openassetclub.com on separate cPanel hosting
- **Connection**: Website fetches live data from VPS using API

```
VPS Bot (72.62.254.237)              cPanel Hosting (openassetclub.com)
├─ main.py (trading)          ←→     ├─ landing_page.html
├─ api_public.py (API)        ←→     └─ dashboard.html
└─ Database (trades, users)   ←→     (fetches data via HTTP)
```

---

## 🚀 QUICK START (5 MINUTES)

### Step 1: Download Files to Your Computer

Download these 3 files from GitHub:
1. `landing_page.html` - Your SAAS homepage
2. `dashboard.html` - Admin dashboard with live stats
3. `api_public.py` - API service (stays on VPS)

```bash
# From your computer:
git clone https://github.com/agencyhouse-lab/openasset-trading-bot.git
cd openasset-trading-bot
# Copy these files to your downloads:
# - landing_page.html
# - dashboard.html
```

---

### Step 2: Upload HTML Files to cPanel

**Option A: Using cPanel File Manager (Easiest)**

1. Log in to cPanel: `openassetclub.com:2082` or `cPanel URL`
2. Find: **File Manager** → **public_html** folder
3. Click: **Upload** button
4. Select: `landing_page.html` and `dashboard.html`
5. Wait for upload to complete ✅

**Option B: Using FTP (More Control)**

1. Download FTP software: FileZilla (free)
2. Connect:
   - Host: `openassetclub.com` (or FTP hostname from cPanel)
   - Username: Your cPanel username
   - Password: Your cPanel password
   - Port: 21
3. Navigate to: `/public_html`
4. Drag and drop: `landing_page.html` and `dashboard.html`
5. Done ✅

**Option C: Using SSH (Advanced)**

```bash
# From your computer:
scp landing_page.html user@openassetclub.com:/public_html/
scp dashboard.html user@openassetclub.com:/public_html/

# Or via cPanel SSH:
ssh user@openassetclub.com
cd /public_html
# (then upload files via SSH)
```

---

### Step 3: Start API on VPS

SSH into your VPS and start the API service:

```bash
# SSH to VPS
ssh root@72.62.254.237

# Go to project directory
cd /root/openasset-trading-bot

# Start API in background
nohup python3 api_public.py > /var/log/openasset_api.log 2>&1 &

# Verify it's running
curl http://localhost:9000/api/public/stats
# Should return JSON data ✅
```

---

### Step 4: Test from Your Browser

Open these URLs in your browser:

**Landing Page:**
```
http://openassetclub.com/landing_page.html
```

**Dashboard:**
```
http://openassetclub.com/dashboard.html
```

Both should load immediately! ✅

---

## 🔧 CONFIGURATION

### If Your VPS IP Changes

Edit the HTML files to update the API URL:

**landing_page.html** (around line 285):
```javascript
// Change this:
const API_URL = 'http://72.62.254.237:9000/api/public';

// To your new IP:
const API_URL = 'http://NEW_VPS_IP:9000/api/public';
```

**dashboard.html** (around line 170):
```javascript
// Change this:
const API_URL = 'http://72.62.254.237:9000/api/public';

// To your new IP:
const API_URL = 'http://NEW_VPS_IP:9000/api/public';
```

Then re-upload to cPanel. ✅

---

## 📊 WHAT EACH FILE DOES

### `landing_page.html` - Your SAAS Homepage
- Beautiful hero section with AI trading pitch
- Features: 6 benefit cards
- Live stats from API (auto-updates)
- Platform showcase: Binance, Alpaca, OANDA, StratLab
- How it works: 4 step walkthrough
- Pricing: 3 subscription tiers
- Call to action: "View Dashboard" button
- **Goal**: Convince visitors to try the bot

### `dashboard.html` - Admin Dashboard
- Overview stats: users, trades, revenue, P&L
- Platform status: all 4 platforms
- Recent trades table: live data
- Bot configuration display
- Auto-refresh every 30 seconds
- Manual refresh button
- Dark professional theme
- **Goal**: Show real metrics to prove it works

### `api_public.py` - VPS API Service
- Runs on VPS at port 9000
- Endpoints:
  - `/api/public/stats` → Overall statistics
  - `/api/public/trades` → Recent trades
  - `/api/public/users` → User count
  - `/api/public/revenue` → Revenue data
  - `/api/public/health` → Bot health
  - `/api/public/config` → Bot configuration
- **Goal**: Provides live data to website

---

## ✅ VERIFYING EVERYTHING WORKS

### Test 1: Check API is Accessible

From your computer, open:
```
http://72.62.254.237:9000/api/public/stats
```

You should see JSON data like:
```json
{
  "status": "operational",
  "platform": {
    "total_users": 460,
    "total_trades_executed": 1000,
    "total_revenue_usd": 5000,
    ...
  }
}
```

If you see data: ✅ API is working!

If error: 
- Check VPS is running API: `curl http://localhost:9000/api/public/stats`
- Check firewall allows port 9000
- Check IP isn't blocked by cPanel

### Test 2: Check Landing Page Loads

Visit:
```
http://openassetclub.com/landing_page.html
```

You should see:
- ✅ Purple gradient header
- ✅ "AI Trading Bot That Works For You 24/7" title
- ✅ Live stats from API (updates every 30s)
- ✅ Features, platforms, pricing visible
- ✅ Beautiful responsive design

### Test 3: Check Dashboard Loads

Visit:
```
http://openassetclub.com/dashboard.html
```

You should see:
- ✅ Dark professional theme
- ✅ Live stats grid (users, trades, revenue)
- ✅ Platform status cards
- ✅ Recent trades table
- ✅ Auto-refresh indicator
- ✅ No errors in browser console

### Test 4: Check Mobile Responsive

Open from phone:
- ✅ Landing page responsive
- ✅ Dashboard responsive
- ✅ All text readable
- ✅ Buttons clickable

---

## 🌐 SETTING UP CUSTOM DOMAIN

### Option 1: Point openassetclub.com to cPanel

In your domain registrar (GoDaddy, Namecheap, etc.):
1. Go to DNS settings
2. Add A record:
   - Type: A
   - Name: @
   - Value: Your cPanel IP (from cPanel → Server Information)
3. Wait 24-48 hours for DNS propagation

Then:
```
http://openassetclub.com/landing_page.html
http://openassetclub.com/dashboard.html
```

### Option 2: Use Subdomain

In cPanel:
1. Go to: Addon Domains or Parked Domains
2. Add: `api.openassetclub.com` → points to VPS
3. Update HTML files to use:
   ```javascript
   const API_URL = 'http://api.openassetclub.com:9000/api/public';
   ```

---

## 🚨 TROUBLESHOOTING

### Problem: "Dashboard shows no data"

**Solution:**
1. Check API is running on VPS:
   ```bash
   curl http://72.62.254.237:9000/api/public/stats
   ```
2. Check browser console for errors (F12 → Console)
3. Check firewall allows port 9000 from your IP
4. Wait 30 seconds for auto-refresh

### Problem: "Stats showing outdated numbers"

**Solution:**
1. Click "🔄 Refresh" button in dashboard
2. Wait 30 seconds for next auto-refresh
3. Check API is responding with fresh data:
   ```bash
   curl http://72.62.254.237:9000/api/public/stats | grep timestamp
   ```

### Problem: "HTML files not uploading to cPanel"

**Solution:**
1. Check file size (should be < 100 KB each)
2. Try different upload method (FTP instead of web uploader)
3. Check file permissions: 644 (cPanel will set this)
4. Clear browser cache and try again

### Problem: "Getting CORS error in console"

**Solution:**
- This should NOT happen (API has CORS enabled)
- Check API is running: `curl http://localhost:9000`
- Restart API: `pkill -f api_public.py && nohup python3 api_public.py &`

### Problem: "Landing page looks different than expected"

**Solution:**
1. Clear browser cache: Ctrl+Shift+Delete (Chrome)
2. Hard refresh: Ctrl+Shift+R
3. Try different browser (Chrome, Firefox, Safari)
4. Check file uploaded correctly (view source)

---

## 📈 CUSTOMIZATION

### Change Stats Numbers (for testing)

Edit your bot database on VPS:
```bash
# SSH to VPS
ssh root@72.62.254.237

# Edit database
nano /root/openasset_club/telegram_bot/database/users.json
# Add more users (bot will count them)

nano /root/openasset_club/telegram_bot/database/trades.json
# Add test trades to show history
```

API will reflect changes immediately on website. ✅

### Change Pricing Display

Edit `landing_page.html`:
```html
<!-- Find this section around line 450 -->
<div class="pricing-card">
    <h3>🎯 COMPLETE</h3>
    <div class="price">$59.92<span style="font-size: 1rem;">/month</span></div>
    
    <!-- Edit price here -->
    <!-- Edit features here -->
</div>
```

Save and re-upload to cPanel.

### Change Colors/Theme

Edit CSS in `landing_page.html` and `dashboard.html`:
```css
/* Find these lines and change colors */
--primary-color: #667eea;  /* Purple */
--secondary-color: #764ba2; /* Dark purple */
--background: #0f172a;      /* Dark blue */
--text: #e2e8f0;           /* Light gray */
```

---

## 🔐 SECURITY NOTES

✅ **Safe:**
- HTML files are static (no database access)
- API is read-only (no sensitive data)
- No API key stored in HTML files
- CORS allows any domain (public data)

⚠️ **Important:**
- Never put real API keys in HTML files
- API only serves public stats (no user data)
- Sensitive operations stay on VPS
- Database files only on VPS (not in web)

---

## 📝 FILE CHECKLIST

Before launching:
- [ ] `landing_page.html` uploaded to cPanel
- [ ] `dashboard.html` uploaded to cPanel
- [ ] `api_public.py` running on VPS
- [ ] API responds to HTTP requests
- [ ] Both HTML files load in browser
- [ ] Stats auto-update (every 30 seconds)
- [ ] Mobile responsive tested
- [ ] No console errors in browser
- [ ] Performance acceptable (< 2 second load)

---

## 🎉 YOU'RE READY!

Once everything is working:

1. **Test with users**: Send landing page link to 10 beta users
2. **Monitor dashboard**: Check stats, trades, revenue daily
3. **Gather feedback**: Ask users what they like/dislike
4. **Optimize**: Improve features based on feedback
5. **Scale**: Add more users, increase marketing
6. **Launch**: Go live with payment processing

---

## 📞 SUPPORT

If anything breaks:

1. **Check logs on VPS:**
   ```bash
   tail -100f /var/log/openasset_api.log
   tail -100f /root/openasset_club/telegram_bot/logs/user_bot.log
   ```

2. **Check API health:**
   ```bash
   curl http://72.62.254.237:9000/api/public/health
   ```

3. **Restart API:**
   ```bash
   pkill -f api_public.py
   nohup python3 /root/openasset-trading-bot/api_public.py > /var/log/openasset_api.log 2>&1 &
   ```

4. **Test from browser console:**
   ```javascript
   fetch('http://72.62.254.237:9000/api/public/stats')
     .then(r => r.json())
     .then(d => console.log(d))
   ```

---

**You're all set! 🚀**
