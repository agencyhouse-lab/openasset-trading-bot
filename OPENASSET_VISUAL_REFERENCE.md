# 🎨 OpenAsset Trading Bot - Visual Quick Reference

## 📊 COLOR PALETTE

```
╔═══════════════════════════════════════════════════════════════╗
║                  PRIMARY COLORS                              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🟢 SUCCESS GREEN           #00FF5F                           ║
║     Usage: Profits, gains, active state, primary buttons      ║
║     RGB: (0, 255, 95)                                        ║
║                                                               ║
║  ⚫ DARK BACKGROUND         #0A0E27                           ║
║     Usage: Main background, page background                   ║
║     RGB: (10, 14, 39)                                        ║
║                                                               ║
║  ⬜ SECONDARY DARK          #1A1F3A                           ║
║     Usage: Cards, containers, sections                        ║
║     RGB: (26, 31, 58)                                        ║
║                                                               ║
║  🔘 ACCENT GRAY             #2A3F5F                           ║
║     Usage: Borders, dividers, secondary elements              ║
║     RGB: (42, 63, 95)                                        ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                   TEXT COLORS                                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ⚪ TEXT PRIMARY            #FFFFFF                           ║
║     Usage: Main text, headings                                ║
║     RGB: (255, 255, 255)                                     ║
║                                                               ║
║  🩶 TEXT SECONDARY          #B0B8C8                           ║
║     Usage: Labels, descriptions, small text                   ║
║     RGB: (176, 184, 200)                                     ║
║                                                               ║
║  ↔️ TEXT TERTIARY           #666B7F                           ║
║     Usage: Disabled text, placeholders                        ║
║     RGB: (102, 107, 127)                                     ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                  STATE COLORS                                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ✅ SUCCESS                 #00FF5F                           ║
║     Usage: Winning trades, completed actions                  ║
║                                                               ║
║  ❌ DANGER / LOSS            #FF4444                           ║
║     Usage: Losing trades, stop loss, errors                   ║
║     RGB: (255, 68, 68)                                       ║
║                                                               ║
║  ⚠️  WARNING / ALERT         #FFB800                           ║
║     Usage: Pending trades, cautions                           ║
║     RGB: (255, 184, 0)                                       ║
║                                                               ║
║  ℹ️  INFO                   #6E9FFF                           ║
║     Usage: Information messages                               ║
║     RGB: (110, 159, 255)                                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Semi-Transparent Variants

```
Success Overlay:    rgba(0, 255, 95, 0.1)  → #00FF5F with 10% opacity
Success Hover:      rgba(0, 255, 95, 0.2)  → for hover states
Border Light:       rgba(0, 255, 95, 0.2)  → for subtle borders
Danger Overlay:     rgba(255, 68, 68, 0.15) → for error backgrounds
```

---

## 🎯 TYPOGRAPHY

### Font Family
```
System Font Stack:
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
Oxygen, Ubuntu, Cantarell, sans-serif
```

### Font Sizes & Weights

```
╔═══════════════════════════════════════════════════════════════╗
║ TYPE          │ SIZE │ WEIGHT │ LINE HEIGHT │ USAGE          ║
╠═══════════════════════════════════════════════════════════════╣
║ H1/Title      │ 18px │ Bold  │ 1.2         │ Screen headers  ║
║ H2/Heading    │ 16px │ Bold  │ 1.2         │ Section titles  ║
║ H3/Subhead    │ 14px │ Bold  │ 1.3         │ Card titles     ║
║ Body Text     │ 12px │ Reg   │ 1.5         │ Main content    ║
║ Small/Label   │ 11px │ Reg   │ 1.4         │ Labels, hints    ║
║ Tiny/Caption  │ 10px │ Reg   │ 1.3         │ Timestamps      ║
║ Number/Code   │ 12px │ Bold  │ 1.4         │ Prices, counts  ║
║ Large Number  │ 36px │ Bold  │ 1.0         │ Balance display ║
║ Monospace     │ 12px │ Bold  │ 1.4         │ Crypto amounts  ║
╚═══════════════════════════════════════════════════════════════╝
```

### Text Styles

```
UPPERCASE LABELS (Small)
Regular Body Text for descriptions and longer content
Bold Numbers for prices and quantities
Monospace for BTCUSDT symbols and amounts
```

---

## 📦 COMPONENT SIZING

### Buttons

```
╔════════════════════════════════════════════════════════╗
║  BUTTON TYPE          │ WIDTH   │ HEIGHT │ PADDING    ║
╠════════════════════════════════════════════════════════╣
║  Primary (Full)       │ 100%    │ 44px   │ 12px       ║
║  Secondary (1/2)      │ calc(50%-4px) │ 40px │ 10px   ║
║  Icon Button          │ 40px    │ 40px   │ 0px        ║
║  Pill Button (Tab)    │ auto    │ 32px   │ 12px       ║
╚════════════════════════════════════════════════════════╝
```

### Cards

```
╔════════════════════════════════════════════════════════╗
║  CARD TYPE            │ WIDTH   │ PADDING │ RADIUS    ║
╠════════════════════════════════════════════════════════╣
║  Balance Card         │ 100%    │ 20px    │ 12px      ║
║  Trade Card           │ 100%    │ 12px    │ 10px      ║
║  Stat Box (1/2)       │ calc(50%-6px) │ 12px │ 10px  ║
║  Section Card         │ 100%    │ 16px    │ 12px      ║
╚════════════════════════════════════════════════════════╝
```

### Spacing (Vertical)

```
Between sections:  16px (lg)
Between cards:     12px (md)
Between elements:  8px (sm)
Inside padding:    12-16px
Header padding:    16px
Footer padding:    12px
```

---

## 🎨 GRADIENT DEFINITIONS

### Primary Balance Card Gradient
```
Direction: 135deg (top-left to bottom-right)
From: #1A1F3A
To: #2A3F5F
Effect: Subtle depth increase
```

### Success Card Gradient
```
Direction: 135deg
From: #1A3F1A (dark green tint)
To: #2A5F2A (lighter green tint)
Border: 1px solid rgba(0, 255, 95, 0.2)
```

### Warning Card Gradient
```
Direction: 135deg
From: #3F2A1A (dark orange tint)
To: #5F3A1A (lighter orange tint)
Border: 1px solid rgba(255, 184, 0, 0.2)
```

### Header Gradient
```
Direction: 135deg (top-left to bottom-right)
From: #00FF5F
To: #00DD5F
Text Color: #0A0E27
Effect: Bold, high contrast
```

---

## 🔘 BUTTON STATES

### Primary Button (Green)

```
DEFAULT:
  Background: #00FF5F
  Text: #0A0E27
  Border: none
  
HOVER:
  Background: #00DD5F
  Text: #0A0E27
  Shadow: 0 4px 12px rgba(0, 255, 95, 0.3)
  Transform: translateY(-2px)
  
ACTIVE:
  Background: #00CC5F
  Scale: 0.98
  
DISABLED:
  Background: #666B7F
  Text: #999
  Cursor: not-allowed
  Opacity: 0.6
```

### Secondary Button (Gray)

```
DEFAULT:
  Background: #2A3F5F
  Text: #FFFFFF
  Border: 1px solid rgba(0, 255, 95, 0.2)
  
HOVER:
  Background: #3A4F7F
  Border: 1px solid rgba(0, 255, 95, 0.5)
  
ACTIVE:
  Background: #4A5F9F
```

### Danger Button (Red)

```
DEFAULT:
  Background: #FF4444
  Text: #FFFFFF
  Border: none
  
HOVER:
  Background: #DD3333
  Shadow: 0 4px 12px rgba(255, 68, 68, 0.3)
  
ACTIVE:
  Background: #CC2222
```

---

## 📐 BORDER & SHADOW STYLES

### Borders

```
Default Card Border:
  1px solid #2A3F5F
  
Light Border (subtle):
  1px solid rgba(0, 255, 95, 0.2)
  
Accent Border (highlight):
  1px solid rgba(0, 255, 95, 0.5)
  
Left Border (alerts):
  3px solid #FF4444 (or accent color)
```

### Shadows

```
Card Shadow:
  0 2px 8px rgba(0, 0, 0, 0.2)
  
Hover Shadow:
  0 4px 12px rgba(0, 255, 95, 0.3)
  
Deep Shadow:
  0 8px 24px rgba(0, 0, 0, 0.4)
  
Glow Effect (success):
  0 0 20px rgba(0, 255, 95, 0.5)
```

---

## 🎯 LAYOUT GRID

### Mobile (320px)

```
┌─────────────────────────┐
│      [Header 64px]      │
├─────────────────────────┤
│   Content               │
│   [16px padding]        │
│                         │
│   - Full width cards    │
│   - Single column       │
│   - Stacked buttons     │
│                         │
│ [16px padding]          │
├─────────────────────────┤
│   [Footer 60px]         │
└─────────────────────────┘
```

### Component Width Reference

```
Full Width Card:    calc(100% - 32px) [16px padding each side]
Half Width Box:     calc(50% - 6px) [in 2-column grid]
Buttons (pair):     calc(50% - 4px) each [8px gap between]
Navigation Icon:    24px size
Content Line:       max-width: 90% (for readability)
```

---

## 🎭 ICON SYSTEM

### Navigation Icons (Bottom Bar)

```
Home:        🏠    (House outline)
Stats:       📊    (Chart/Graph)
Trading:     🤖    (Robot)
Settings:    ⚙️    (Gear)
```

### Action Icons (Buttons)

```
Start:       🚀    (Rocket)
Stop/Pause:  ⏸️    (Pause)
Buy:         🟢    (Green circle)
Sell:        🔴    (Red circle)
Market Data: 📈    (Chart up)
Balance:     💰    (Money bag)
Wallet:      👛    (Wallet)
Settings:    ⚙️    (Gear)
```

### Status Icons

```
Active/Success:     ✅ 🟢
Inactive/Failure:   ❌ 🔴
Warning/Pending:    ⚠️ 🟡
Info:               ℹ️ 💡
Monitoring:         👁️ 📊
Executing:          ⚡ 🚀
```

### Asset Icons

```
Bitcoin:            ₿ 📍
Ethereum:           Ξ 
Binance Coin:       🟡 (or custom)
Solana:             ◎
USDT:               💵
Generic Crypto:     📊
```

---

## 🔄 ANIMATION SPECIFICATIONS

### Fade Transition

```
Easing: ease-in
Duration: 0.3s
Opacity: from 0 to 1
Usage: Screen changes
```

### Button Hover

```
Transform: translateY(-2px)
Duration: 0.3s
Easing: ease
Shadow: 0 4px 12px rgba(color, 0.3)
```

### Loading State

```
Animation: Rotating
Duration: 1s
Iteration: infinite
Color: #00FF5F
```

### Value Change Highlight

```
Background: rgba(0, 255, 95, 0.2)
Duration: 2s
Fade-out: ease-out
```

---

## 📏 SPACING SCALE

```
Multiplier   │ Pixels │ Usage
─────────────┼────────┼──────────────────────
xs          │ 4px    │ Extra small gaps
sm          │ 8px    │ Small gaps, dividers
md          │ 12px   │ Standard spacing
lg          │ 16px   │ Large spacing, padding
xl          │ 20px   │ Extra large gaps
```

### Common Spacing Values

```
Header padding:           16px
Card padding:            12-20px
Button padding:          12px (V) × 16px (H)
Section margin:          16px top
Element gap:             8-12px
Screen edge padding:     16px
Navigation bar height:   60px
Header height:           64px
```

---

## 📱 BREAKPOINT STRATEGY

### Mobile First (320px)
- Default layout
- Full-width components
- Single column
- Bottom navigation

### Tablet+ (480px+)
- 2-column layouts possible
- Wider charts
- Side-by-side cards
- Can add more options

### Desktop (1024px+)
- Multi-column dashboard
- Large charts
- Sidebar navigation
- Advanced features

---

## ✨ VISUAL HIERARCHY

### Primary (Most Important)
- Large balance amount
- Active trade symbol
- Current profit/loss
- Primary action button

### Secondary (Important)
- Entry/exit prices
- Performance metrics
- Secondary buttons
- Card titles

### Tertiary (Supporting)
- Labels
- Timestamps
- Descriptions
- Help text

---

## 🎨 COLOR COMBINATIONS

### Success State
```
Background: #1A3F1A (dark green)
Text: #FFFFFF (white)
Accent: #00FF5F (bright green)
Border: rgba(0, 255, 95, 0.3)
```

### Error State
```
Background: #3F1A1A (dark red)
Text: #FFB8B8 (light red)
Accent: #FF4444 (bright red)
Border: 3px solid #FF4444
```

### Warning State
```
Background: #3F2A1A (dark orange)
Text: #FFD9B8 (light orange)
Accent: #FFB800 (bright orange)
Border: rgba(255, 184, 0, 0.3)
```

### Neutral State
```
Background: #2A3F5F (gray)
Text: #B0B8C8 (light gray)
Accent: #4A5F9F (lighter gray)
Border: 1px solid #3A4F7F
```

---

## 📋 COMPONENT CHECKLIST

Use this when creating new screens:

```
☐ Background: #0A0E27
☐ Header: Green gradient
☐ Cards: #1A1F3A with #2A3F5F border
☐ Text: #FFFFFF (primary), #B0B8C8 (secondary)
☐ Numbers: Monospace, bold, color-coded
☐ Buttons: Match button style guide
☐ Spacing: Follow spacing scale
☐ Icons: Use standard emoji set
☐ Shadows: Apply subtle shadows
☐ Borders: 1px solid #2A3F5F
☐ Hover states: Implemented
☐ Mobile responsive: 320px tested
☐ Loading states: Shown (if applicable)
☐ Error messages: Red styling
☐ Success messages: Green styling
```

---

## 🎬 SCREEN REFERENCE CHECKLIST

### Home Screen
- [ ] Balance card (prominent)
- [ ] Performance card (green)
- [ ] Action buttons (2 columns)
- [ ] Open positions (3+ trades)
- [ ] Bottom navigation

### Auto Trading Screen
- [ ] Bot status badge
- [ ] Performance chart
- [ ] Settings grid (4 stats)
- [ ] Statistics summary
- [ ] Start/Pause buttons

### Manual Trading Screen
- [ ] Pair selector buttons
- [ ] Custom symbol input
- [ ] Order type tabs
- [ ] Quantity input
- [ ] Risk/reward display
- [ ] Execute button

### Statistics Screen
- [ ] Period selector tabs
- [ ] Performance chart
- [ ] Metrics grid
- [ ] Trade quality stats
- [ ] Timing stats

### Settings Screen
- [ ] Exchange connections
- [ ] Notification toggles
- [ ] API management
- [ ] Support links
- [ ] Save button

---

## 🚀 QUICK START GUIDE

### Creating a New Card
```html
<div style="
  background: #1A1F3A;
  border: 1px solid #2A3F5F;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
">
  Content here
</div>
```

### Creating a Button
```html
<button style="
  background: #00FF5F;
  color: #0A0E27;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 600;
  width: 100%;
">
  Button Text
</button>
```

### Creating a Stat Box
```html
<div style="
  background: #1A1F3A;
  border: 1px solid #2A3F5F;
  border-radius: 10px;
  padding: 12px;
  text-align: center;
">
  <div style="color: #B0B8C8; font-size: 11px;">LABEL</div>
  <div style="color: #00FF5F; font-size: 18px; font-weight: bold;">VALUE</div>
</div>
```

---

## 📞 FINAL NOTES

✅ **Design is optimized for:**
- Telegram Bot UI (message-based)
- Mobile devices (320px+)
- Real-time data display
- Quick user interactions
- Professional appearance
- Gaming aesthetic

❌ **Design avoids:**
- Complex animations (slow on mobile)
- Micro-interactions (confusing)
- Cluttered layouts
- Small text (<11px)
- Bright backgrounds (low contrast)
- Excessive colors (too many hues)

🎯 **Best practices followed:**
- ✅ High contrast (WCAG AA)
- ✅ Consistent spacing
- ✅ Predictable interactions
- ✅ Fast load times
- ✅ Touch-friendly (44px buttons)
- ✅ Clear information hierarchy

---

**Design System Version:** 1.0  
**Last Updated:** May 27, 2026  
**Status:** Ready for Implementation  
**Approval Status:** Pending Review
