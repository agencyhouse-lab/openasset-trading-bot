# 🎨 OPENASSET TRADING BOT - UI/UX DESIGN SYSTEM

## COLOR SCHEME

```
Primary Green: #00FF5F (Neon Green - Highlights, Active states)
Dark Background: #0A0E27 (Deep Dark Blue/Black)
Secondary Dark: #1A1F3A (Slightly lighter dark background)
Accent Gray: #2A3F5F (Secondary element background)
Text Primary: #FFFFFF (White text)
Text Secondary: #B0B8C8 (Light gray for secondary info)
Success: #00FF5F (Green - Profits)
Warning: #FFB800 (Orange - Alerts)
Danger: #FF4444 (Red - Losses, Stop Loss)
Neutral Gray: #666B7F (Neutral text)
```

## DESIGN PRINCIPLES

✅ Minimal, Clean Layout
✅ Data-Focused (numbers first)
✅ Real-time Updates
✅ Easy Navigation
✅ Professional Gaming Aesthetic
✅ High Contrast for Readability
✅ Mobile-First (Telegram width ~320px)

---

## 🏠 SCREEN 1: HOME DASHBOARD

```
┌─────────────────────────────────┐
│ ← OPENASSET         ⚙️ ⚙️ • ⋮   │
├─────────────────────────────────┤
│                                 │
│    💰 YOUR BALANCE              │
│    ━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│    $2,450.00  USDT              │
│                                 │
│    BTC: 0.05  |  ETH: 1.2       │
│                                 │
├─────────────────────────────────┤
│ 🤖 AUTO TRADE  |  👆 MANUAL     │
│ ✅ ACTIVE      |  📊 DATA       │
├─────────────────────────────────┤
│                                 │
│  📈 Today Performance           │
│  ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░    │
│  +1.23%  P&L: +$30.00          │
│                                 │
├─────────────────────────────────┤
│ 🟢 OPEN POSITIONS: 3            │
│                                 │
│ BTCUSDT  $45K  +0.5% (+$225)   │
│ ETHUSDT  $2.5K -0.2% (-$5)     │
│ BNBUSDT  $650  +1.2% (+$7.80)  │
│                                 │
├─────────────────────────────────┤
│ 📊 STATS │ 📋 HISTORY │ ⚙️ MORE │
└─────────────────────────────────┘
```

---

## 🤖 SCREEN 2: AUTO TRADING MODE

```
┌─────────────────────────────────┐
│ ← AUTO TRADING        ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  BOT STATUS: 🟢 ACTIVE          │
│  Current Price: $45,936.72 BTC  │
│                                 │
│  ┌─────────────────────────────┐│
│  │ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ││
│  │ (Line Chart - 24h trend)     ││
│  │ ▁▁▁▁▂▂▃▃▄▄▅▅▆▆▇▇██████████▁││
│  └─────────────────────────────┘│
│                                 │
│  ⏱️  Frequency: 5 minutes        │
│  📊 Trade Mode: Market Order    │
│                                 │
│  Safety Settings:               │
│  🛑 Max Loss: 0.5%              │
│  🎯 Take Profit: 3-5%           │
│  ⚙️  Max Trades: 3              │
│                                 │
├─────────────────────────────────┤
│                                 │
│ ✅ SUCCESSFUL TRADES: 31        │
│ ❌ FAILED TRADES: 6             │
│ 📊 Win Rate: 83.7%              │
│ 💰 Total P&L: +$850.25          │
│                                 │
├─────────────────────────────────┤
│  [🚀 START BOT]  [⏸️ PAUSE]     │
│  [⚙️ SETTINGS]   [📊 HISTORY]   │
└─────────────────────────────────┘
```

---

## 👆 SCREEN 3: MANUAL TRADING

```
┌─────────────────────────────────┐
│ ← MANUAL TRADING      ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  SELECT TRADING PAIR            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  [📈 BTCUSDT]                   │
│  Current: $45,936.72            │
│  24h Change: +2.5%              │
│  High: $46,500  Low: $44,800    │
│                                 │
├─────────────────────────────────┤
│                                 │
│  QUICK TRADE                    │
│                                 │
│  Order Type:                    │
│  ◉ Market Order  ○ Limit        │
│                                 │
│  Side:                          │
│  [🟢 BUY] [🔴 SELL]            │
│                                 │
│  Quantity: [  0.01  ] BTC       │
│                                 │
│  Entry: $45,936.72              │
│  Stop Loss: $45,719 (-0.5%)     │
│  Take Profit: $47,315 (+3%)     │
│                                 │
├─────────────────────────────────┤
│                                 │
│  Risk: $10.80  |  Reward: $46.07│
│  Ratio: 1:4.26                  │
│                                 │
│  [✅ EXECUTE TRADE]             │
│  [❌ CANCEL]                    │
│                                 │
└─────────────────────────────────┘
```

---

## 📊 SCREEN 4: MARKET DATA

```
┌─────────────────────────────────┐
│ ← MARKET DATA         ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  LIVE PRICES                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  ₿ BITCOIN                      │
│  $45,936.72                     │
│  🟢 +2.5% (24h)                │
│  High: $46,500 | Low: $44,800  │
│  Vol: 25.3K BTC                 │
│                                 │
│  Ξ ETHEREUM                     │
│  $2,080.33                      │
│  🔴 -1.2% (24h)                │
│  High: $2,150 | Low: $2,010    │
│  Vol: 856K ETH                  │
│                                 │
│  🟡 BNB                         │
│  $643.45                        │
│  🟢 +0.8% (24h)                │
│  High: $655 | Low: $625        │
│                                 │
│  ◎ SOL                          │
│  $148.92                        │
│  🟢 +3.2% (24h)                │
│  High: $152 | Low: $141        │
│                                 │
├─────────────────────────────────┤
│  🔄 Refresh  |  ⭐ Favorites    │
│  📊 Charts   |  ⚙️  Settings    │
└─────────────────────────────────┘
```

---

## 📋 SCREEN 5: TRADE HISTORY

```
┌─────────────────────────────────┐
│ ← TRADE HISTORY       ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  TODAY: 7 TRADES  P&L: +$125.40 │
│                                 │
│  ✅ BTCUSDT                     │
│  BUY @ $45,900 → SELL @ $46,045│
│  Profit: +0.31% (+$145)         │
│  27.05.2026 17:46               │
│                                 │
│  ✅ ETHUSDT                     │
│  BUY @ $2,075 → SELL @ $2,083  │
│  Profit: +0.38% (+$64)          │
│  27.05.2026 17:29               │
│                                 │
│  ❌ BNBUSDT                     │
│  BUY @ $645 → CLOSE @ $643      │
│  Loss: -0.31% (-$12.80)         │
│  27.05.2026 16:38               │
│                                 │
│  ✅ BTCUSDT                     │
│  BUY @ $45,850 → SELL @ $45,978│
│  Profit: +0.27% (+$128.50)      │
│  27.05.2026 16:15               │
│                                 │
├─────────────────────────────────┤
│  Filter: [All] [Win] [Loss]     │
│  [Older Trades ▼]               │
│                                 │
│  📊 Stats  |  📈 Export         │
└─────────────────────────────────┘
```

---

## 📊 SCREEN 6: STATISTICS

```
┌─────────────────────────────────┐
│ ← STATISTICS          ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  PERFORMANCE PERIOD             │
│  [24h] [3d] [7d] [1m] [All]     │
│                                 │
│  📈 CHART (Last 24h)            │
│  ┌─────────────────────────────┐│
│  │ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ││
│  │ (Line chart showing growth)  ││
│  │ Return: +3.45%               ││
│  └─────────────────────────────┘│
│                                 │
│  KEY METRICS                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  🎯 Total Trades:    54         │
│  ✅ Winning:         31 (57%)   │
│  ❌ Losing:          23 (43%)   │
│  📊 Win Rate:        57.4%      │
│                                 │
│  💰 PROFIT METRICS              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  Total P&L:      +$1,248.50     │
│  Avg Win:        +$42.30        │
│  Avg Loss:       -$18.90        │
│  Profit Factor:  2.24x          │
│  Best Trade:     +3.45% (+$182) │
│  Worst Trade:    -0.45% (-$45)  │
│                                 │
│  ⏱️ TRADE TIMING                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  Avg Trade Duration: 15 min     │
│  Fastest Trade:      2 min      │
│  Longest Trade:      2h 30m     │
│                                 │
│  [📥 Export Data]               │
│                                 │
└─────────────────────────────────┘
```

---

## ⚙️ SCREEN 7: SETTINGS & API

```
┌─────────────────────────────────┐
│ ← SETTINGS            ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  TRADING PREFERENCES            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  Trade Frequency:               │
│  [1m] [5m] [15m] [30m] [60m]   │
│                                 │
│  Risk per Trade:                │
│  [Max Loss: 0.5%] ◀─────────▶  │
│                                 │
│  Take Profit:                   │
│  [Min: 3%] [Max: 5%]           │
│                                 │
│  Max Open Trades:               │
│  [◀─ 3 ──▶]                     │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  CONNECTED EXCHANGES            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  💰 BINANCE                     │
│  ✅ Connected & Active          │
│  Updated: 27.05.2026 19:47      │
│  [Edit] [Disconnect]            │
│                                 │
│  📈 ALPACA                      │
│  ⚠️ Need Setup                  │
│  [Add API] [Setup Guide]        │
│                                 │
│  🌍 eTORO                       │
│  ⚠️ Need Setup                  │
│  [Add API] [Setup Guide]        │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                 │
│  NOTIFICATIONS                  │
│  🔔 Trade Alerts: [ON/OFF]      │
│  📊 Daily Report: [ON/OFF]      │
│  ⚠️ Loss Alert: [ON/OFF]        │
│                                 │
│  [💾 Save Changes]              │
│                                 │
└─────────────────────────────────┘
```

---

## 📱 SCREEN 8: LIVE TRADING NOTIFICATIONS

```
┌─────────────────────────────────┐
│ ← NOTIFICATIONS       ⚙️ • ⋮    │
├─────────────────────────────────┤
│                                 │
│  TODAY                          │
│                                 │
│  ✅ BTCUSDT TRADE CLOSED       │
│  🎯 Prediction: Successful      │
│  📉 Price DOWN to $75,869       │
│  ✅ Profit: +0.15%              │
│  27.05.2026 18:30               │
│                                 │
│  ✅ ETHUSDT TRADE CLOSED       │
│  🎯 Prediction: Successful      │
│  📈 Price UP to $2,084          │
│  ✅ Profit: +0.18%              │
│  27.05.2026 18:02               │
│                                 │
│  ❌ BNBUSDT TRADE CLOSED       │
│  🎯 Prediction: Failed          │
│  📈 Price UP to $644            │
│  ❌ Loss: -0.20%                │
│  27.05.2026 16:38               │
│                                 │
│  📊 DAILY REPORT               │
│  🎯 7 Trades | 5 Win | 2 Loss  │
│  📈 Today P&L: +$125.40         │
│  27.05.2026 08:00               │
│                                 │
│  ⚠️ HIGH VOLATILITY ALERT      │
│  Bitcoin showing high activity  │
│  Consider reducing trade size   │
│  27.05.2026 07:15               │
│                                 │
│  [Clear All] [Settings]         │
│                                 │
└─────────────────────────────────┘
```

---

## 🎨 DESIGN ELEMENTS

### Typography

```
Headlines: Bold, 16-18px (#FFFFFF)
Subheads: Bold, 13-14px (#B0B8C8)
Body Text: Regular, 12px (#FFFFFF)
Small Text: Regular, 11px (#B0B8C8)
Numbers: Monospace, Bold (#00FF5F for gains, #FF4444 for losses)
```

### Buttons & Controls

```
Primary Button: 
  🟢 Background: #00FF5F
  Text: #0A0E27 (Dark)
  Width: Full or [TEXT]
  Height: 44px
  Border Radius: 8px
  
Secondary Button:
  ⚪ Background: #2A3F5F
  Text: #FFFFFF
  Width: Full or [TEXT]
  Height: 44px
  Border Radius: 8px

Danger Button:
  🔴 Background: #FF4444
  Text: #FFFFFF
  Width: Full or [TEXT]
  Height: 44px
  Border Radius: 8px

Tab/Selector:
  Active: #00FF5F text, underline
  Inactive: #B0B8C8 text
```

### Icons Used

```
Home: 🏠
Trading: 🤖 👆 📊
Balance: 💰
Settings: ⚙️
History: 📋 📈
Stats: 📊
Active: 🟢
Inactive: ⚫
Profit: ✅ 📈 🟢
Loss: ❌ 📉 🔴
Warning: ⚠️
Info: ℹ️
Settings: ⚙️
Clock: ⏱️
Chart: 📈
Money: 💵 💰
Bitcoin: ₿ 📍
Ethereum: Ξ
Alert: 🔔
Stop: 🛑
Pause: ⏸️
Start: 🚀
Remove: ❌ ✕
Back: ←
Menu: ⋮
Refresh: 🔄
```

### Spacing & Layout

```
Screen Width: 320px (Telegram mobile width)
Padding: 12-16px sides, 8-12px top/bottom
Card Spacing: 8px
Element Gap: 12px
Section Gap: 16px
Line Height: 1.5-1.8
```

### Chart Style

```
Line Chart:
  Color: #00FF5F (green)
  Background: Gradient #00FF5F15 (transparent)
  Grid: Subtle #2A3F5F
  Candle/Bar: Green for up, Red for down
  
Stats Display:
  All numbers with 2 decimals
  Percentage with % symbol
  Currency with $ prefix
  Large numbers with commas
```

---

## 🔄 COMPONENT EXAMPLES

### Balance Card

```
┌──────────────────────┐
│ 💰 YOUR BALANCE      │
│ ━━━━━━━━━━━━━━━━━━  │
│ $2,450.00  USDT      │
│                      │
│ BTC: 0.05           │
│ ETH: 1.2            │
│ Etc.                │
└──────────────────────┘
```

### Trade Card

```
┌──────────────────────┐
│ ✅ BTCUSDT           │
│ Entry: $45K          │
│ P&L: +0.5% (+$225)  │
│ [Close Trade] [Edit] │
└──────────────────────┘
```

### Stat Box

```
┌──────────────────────┐
│ Total Trades: 54     │
│ Win Rate: 57.4%      │
│ Total P&L: +$1,248.50│
└──────────────────────┘
```

### Alert Box

```
┌──────────────────────┐
│ ⚠️  HIGH VOLATILITY   │
│ Bitcoin showing      │
│ unusual activity     │
└──────────────────────┘
```

---

## 📏 RESPONSIVE BEHAVIOR

- **Mobile (320px)**: Single column, full-width elements
- **Tablet (480px)**: Can display 2-column layouts where appropriate
- **Desktop**: Wider charts, side panels (if adapted)

---

## 🎯 INTERACTION FLOWS

### Trading Flow
1. User clicks "Manual Trade"
2. Selects pair
3. Chooses order type (Market/Limit)
4. Sets quantity
5. Reviews risk/reward
6. Confirms trade
7. Gets notification

### Stats View
1. User clicks "Statistics"
2. Selects time period (24h/3d/7d/1m/All)
3. Views chart
4. Scrolls through metrics
5. Can export data

### Settings
1. User clicks Settings
2. Adjusts trading parameters
3. Manages API connections
4. Sets notifications
5. Saves changes

---

## 🚀 NEXT PHASE UPDATES

As features expand, these screens will be added:

- [ ] Advanced Trading (Stop Loss, Take Profit editing)
- [ ] Portfolio View (Asset allocation pie chart)
- [ ] Backtesting Results
- [ ] Strategy Builder
- [ ] Risk Calculator
- [ ] News Feed
- [ ] Community Features
- [ ] Referral Dashboard

---

## 📝 IMPLEMENTATION NOTES

This design is optimized for:
✅ Telegram Bot inline buttons
✅ Message-based UI updates
✅ Real-time data refresh
✅ Mobile screens (vertical scrolling)
✅ Quick interactions
✅ Minimal loading time

All text is emoji + ASCII art compatible for maximum compatibility across devices.
