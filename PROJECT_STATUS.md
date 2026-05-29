# OpenAsset Trading Bot — Project Status
**Last updated:** 2026-05-29 (after Phase 4f)
**Git tag:** `v1.0-strategy-lab-working`

---

## SYSTEM OVERVIEW

Telegram SaaS trading platform with 3 trading venues:
- **Binance** — live crypto (real money in LIVE mode)
- **Alpaca** — live US stocks/ETFs
- **Strategy Lab** — practice engine, 40+ symbols, 6 asset classes, real prices

### Infrastructure
- **VPS:** Hostinger Ubuntu 22.04, `72.62.254.237`, `root@maxhive.cloud`
- **User Bot:** `@openasset_club_bot` | Token `8806957280:AAGMOvWRllb2LNmOm4TVcigoU63_8GWhhCU`
- **Admin Bot:** `@openasset_admin_bot` | Token `8759490386:AAGy3QzviccZzRkXHYmD7EHYtICvToQO3yU`
- **Admin User ID:** `5587885687` (Sunny / @marufsunny, Myanmar UTC+7)
- **GitHub:** `https://github.com/agencyhouse-lab/openasset-trading-bot` (public)
- **Python:** 3.10.12

### Bot directories
```
/root/openasset_club/telegram_bot/   ← USER BOT (running)
  main.py                            ← host bot (DO NOT overwrite, only patch)
  trading_dashboard.py               ← all dashboard logic (our code)
  binance_client.py                  ← Binance live trading
  alpaca_client.py                   ← Alpaca stocks trading
  openasset_feeds.py                 ← multi-asset price feeds
  openasset_engine.py                ← paper/practice trading engine + SL/TP monitor
  database/
    users.json, subscriptions.json, payments.json
    accounts.json                    ← API keys + live_mode flag + paused flag
    trades.json                      ← all trades (live + practice + strategy lab)
    openasset_accounts.json          ← Strategy Lab accounts (positions, cash, trades)
  logs/user_bot.log

/root/openasset_admin_bot/admin_bot.py    ← ADMIN BOT (running)
/root/openasset-trading-bot/             ← git clone (deploy source)
/root/openasset_backups/                 ← timestamped tarballs from backup.sh
```

---

## WORKING FEATURES (confirmed in production)

### User Bot
- ✅ /start with 📊 Trading Dashboard button
- ✅ Subscription plans: ATBOT $9.99 / BTBOT $9.99 / COMPLETE $59.92
- ✅ Crypto payment flow (BTC, ETH/BNB, USDT-TRC20)
- ✅ 30-day auto-expiry on subscriptions

### Trading Dashboard (/trading)
- ✅ 8-screen dashboard: Home, Auto, Manual, Market, History, Stats, Settings, Psychology
- ✅ 🔴 LIVE MODE toggle for Binance crypto
- ✅ ⏸ Per-platform pause/resume (Binance, Alpaca)
- ✅ 🛑 STOP ALL emergency button
- ✅ 🏠 Main Menu button (bulletproof own callback `td_mainmenu`)
- ✅ `back_home` intercepted universally — fixes Help/FAQ/Guide back buttons
- ✅ Admin notified on every LIVE money trade
- ✅ Safe defaults: 0.5% SL, 3% TP, 1% risk, $50 max/trade

### Binance (crypto)
- ✅ Live BTC/ETH/BNB/SOL prices from Binance API
- ✅ Market BUY in LIVE mode (real money, $50 cap)
- ✅ Withdraw-permission guard on key verification
- ✅ Friendly error for -2015 (explains exactly how to fix Spot permission + IP whitelist)

### Alpaca (US stocks/ETFs)
- ✅ Auto-detects paper vs live keys
- ✅ SPY/QQQ/GLD/USO/IWM/DIA with live prices
- ✅ Notional (fractional) orders
- ✅ clear "No position to sell" error

### Strategy Lab (OpenAsset Internal engine)
- ✅ 40+ symbols across 6 classes (crypto, stocks, ETFs, forex, commodities, indexes)
- ✅ $10,000 practice balance, $50/trade, $1,000 max
- ✅ Real prices: CoinGecko (crypto) + Yahoo Finance (everything else)
- ✅ 30s price cache + stale-on-error fallback
- ✅ Background SL/TP monitor (daemon thread, polls every 30s)
- ✅ Auto-sets 0.5% SL + 3% TP on every buy
- ✅ Market-hours detection: shows "closed, opens in Xh Ym" BEFORE user tries BUY
- ✅ BUY button disabled when market closed
- ✅ Reset preserves trade history (only clears positions + cash)
- ✅ Portfolio view with unrealized P&L

---

## DEPLOYMENT PATTERN

**One command (safe, idempotent, auto-rollback on syntax error):**
```bash
cd /root/openasset-trading-bot && git pull origin main && bash install_trading_dashboard.sh
```

**Backup anytime:**
```bash
bash /root/openasset-trading-bot/backup.sh
```

**Rollback to v1.0:**
```bash
cd /root/openasset-trading-bot
git checkout v1.0-strategy-lab-working
bash install_trading_dashboard.sh
```

---

## KNOWN USER CREDENTIALS

| Service | Credential | Status |
|---|---|---|
| Binance | API key stored in accounts.json | live_mode=False by default |
| Alpaca | Keys stored in accounts.json | LIVE keys ($248 real money) |
| Wallets | BTC `13EVpMB2...`, ETH/BNB `0x1ee7...`, USDT-TRC20 `TMLcCN...` | for payment receipt |

---

## HONEST SCOPE NOTES

- **eToro:** NOW HAS A PUBLIC API (launched Oct 2025). REST at `https://public-api.etoro.com/api/v1/`.
  Keys from `api-portal.etoro.com`. Auth: `x-api-key` + `x-user-key` headers.
  Supports stocks, crypto, ETFs, forex, indices, commodities. Both demo + real money.
  **→ Phase 5 target**

- **OANDA:** Best forex broker with free REST API. Practice and live accounts.
  Base URL `https://api-fxpractice.oanda.com/v3/`. Token-based auth.
  **→ Phase 5 target alongside eToro**

- **Exness:** Needs MetaTrader 5 on Windows VPS (their MT5 bridge). Linux not supported.
  Possible but requires separate Windows VPS + complex setup. Deferred indefinitely.

- **Real SL/TP on Binance/Alpaca:** Strategy Lab has real SL/TP enforcement (background monitor).
  For Binance live: needs OCO bracket orders or extending monitor thread to external positions.
  For Alpaca live: bracket orders available at order creation.
  **→ Phase 5 or standalone task**

- **Auto-trading engine (AI signals):** Phase 4 was SL/TP enforcement. Phase 5 proper is
  the AI signal generator with RSI/MACD/BB triggers. NOT shipped yet.

- **REST API for other businesses:** FastAPI server on port 8001 with API key auth.
  Wraps Strategy Lab engine for third-party integration.
  **→ Phase 6 target**

---

## FILE ROLES

| File | Purpose | Touch? |
|---|---|---|
| `main.py` (VPS) | HOST BOT — payments, subs, platform selection | Patched only (never overwrite) |
| `trading_dashboard.py` | All dashboard screens + callback routing | Our main file |
| `binance_client.py` | Binance REST wrapper + safety guards | Stable |
| `alpaca_client.py` | Alpaca trading client + auto paper/live detect | Stable |
| `openasset_feeds.py` | Multi-asset price aggregator + market hours | Stable |
| `openasset_engine.py` | Practice trading engine + SL/TP monitor | Stable |
| `install_trading_dashboard.sh` | Single-command deployer + patcher + rollback | Update when adding modules |
| `backup.sh` | Create timestamped tarball backup | Stable |
| `diagnose.sh` | Diagnostic dump of main.py structure | Utility only |

---

## NEXT PHASES

### Phase 5 — New Platforms (recommended order)
1. **eToro client** (`etoro_client.py`)
   - REST `https://public-api.etoro.com/api/v1/`
   - Auth: `x-api-key` + `x-user-key` (user gets from api-portal.etoro.com)
   - Supports: stocks, crypto, ETFs, forex, commodities, indexes
   - Both demo ($200 min deposit claimed) and real money
   - Dashboard integration: new `et_` callback prefix

2. **OANDA forex** (`oanda_client.py`)
   - Free practice account, live available
   - REST: `api-fxpractice.oanda.com/v3/`
   - 70+ currency pairs, metals, indices

3. **Real SL/TP on Binance** — OCO bracket orders after market buy

### Phase 6 — REST API for third-party businesses
- FastAPI on port 8001
- API key auth, rate limiting
- Endpoints: /price /account /orders /positions /history
- Wraps Strategy Lab engine

### Phase 7 — AI signal engine
- Technical indicators: RSI, MACD, Bollinger Bands
- Signal generation → auto-execute in LIVE or Strategy Lab
- Background worker with configurable strategy

---

## ADMIN BOT
- Receives notifications on every LIVE money trade
- URL: `@openasset_admin_bot`
- Running at `/root/openasset_admin_bot/admin_bot.py`
