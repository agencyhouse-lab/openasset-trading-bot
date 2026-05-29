#!/usr/bin/env python3
"""
OpenAsset Price Feed Aggregator
================================

Unified price feed for 6 asset classes, using only FREE public APIs:

  * Crypto       → CoinGecko (no API key, 50 calls/min free)
  * Stocks/ETFs  → Yahoo Finance (yfinance)
  * Forex        → Yahoo Finance (=X suffix)
  * Commodities  → Yahoo Finance futures (=F suffix)
  * Indexes      → Yahoo Finance (^ prefix)

30-second in-memory cache to stay well within rate limits.
Designed for paper-trading where seconds-stale prices are acceptable.
"""

import time
import logging
from typing import Optional, Tuple, Dict, List

import requests

logger = logging.getLogger(__name__)

# ─── Symbol registry: friendly name → (asset_class, feed_symbol, display) ───
SYMBOL_REGISTRY: Dict[str, Tuple[str, str, str]] = {
    # ── Crypto (CoinGecko IDs) ──────────────────────────────────────────────
    "BTC":   ("crypto", "bitcoin",      "Bitcoin"),
    "ETH":   ("crypto", "ethereum",     "Ethereum"),
    "BNB":   ("crypto", "binancecoin",  "BNB"),
    "SOL":   ("crypto", "solana",       "Solana"),
    "XRP":   ("crypto", "ripple",       "XRP"),
    "ADA":   ("crypto", "cardano",      "Cardano"),
    "DOGE":  ("crypto", "dogecoin",     "Dogecoin"),
    "MATIC": ("crypto", "matic-network","Polygon"),

    # ── US Stocks (yfinance) ────────────────────────────────────────────────
    "AAPL":  ("stock", "AAPL",  "Apple"),
    "TSLA":  ("stock", "TSLA",  "Tesla"),
    "MSFT":  ("stock", "MSFT",  "Microsoft"),
    "GOOGL": ("stock", "GOOGL", "Alphabet"),
    "AMZN":  ("stock", "AMZN",  "Amazon"),
    "NVDA":  ("stock", "NVDA",  "NVIDIA"),
    "META":  ("stock", "META",  "Meta"),

    # ── ETFs (yfinance) ─────────────────────────────────────────────────────
    "SPY":   ("etf", "SPY", "S&P 500 ETF"),
    "QQQ":   ("etf", "QQQ", "Nasdaq 100 ETF"),
    "IWM":   ("etf", "IWM", "Russell 2000 ETF"),
    "DIA":   ("etf", "DIA", "Dow Jones ETF"),
    "VTI":   ("etf", "VTI", "Total Market ETF"),

    # ── Forex (yfinance =X) ─────────────────────────────────────────────────
    "EURUSD": ("forex", "EURUSD=X", "EUR/USD"),
    "GBPUSD": ("forex", "GBPUSD=X", "GBP/USD"),
    "USDJPY": ("forex", "USDJPY=X", "USD/JPY"),
    "AUDUSD": ("forex", "AUDUSD=X", "AUD/USD"),
    "USDCHF": ("forex", "USDCHF=X", "USD/CHF"),
    "USDCAD": ("forex", "USDCAD=X", "USD/CAD"),
    "NZDUSD": ("forex", "NZDUSD=X", "NZD/USD"),

    # ── Commodities (yfinance futures =F) ──────────────────────────────────
    "GOLD":   ("commodity", "GC=F", "Gold"),
    "SILVER": ("commodity", "SI=F", "Silver"),
    "OIL":    ("commodity", "CL=F", "Crude Oil"),
    "NATGAS": ("commodity", "NG=F", "Natural Gas"),
    "COPPER": ("commodity", "HG=F", "Copper"),
    "WHEAT":  ("commodity", "ZW=F", "Wheat"),

    # ── Indexes (yfinance ^) ────────────────────────────────────────────────
    "SP500":  ("index", "^GSPC", "S&P 500"),
    "NASDAQ": ("index", "^IXIC", "Nasdaq Composite"),
    "DOW":    ("index", "^DJI",  "Dow Jones"),
    "VIX":    ("index", "^VIX",  "Volatility Index"),
    "FTSE":   ("index", "^FTSE", "FTSE 100"),
    "NIKKEI": ("index", "^N225", "Nikkei 225"),
}

ASSET_CLASSES = ["crypto", "stock", "etf", "forex", "commodity", "index"]

# ─── Cache ──────────────────────────────────────────────────────────────────
_CACHE: Dict[str, Tuple[float, float]] = {}  # symbol -> (price, timestamp)
CACHE_TTL = 30  # seconds


def get_symbol_info(symbol: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (asset_class, feed_symbol, display_name) or (None, None, None)."""
    return SYMBOL_REGISTRY.get(symbol.upper(), (None, None, None))


def list_symbols(asset_class: Optional[str] = None) -> List[str]:
    """List supported symbols, optionally filtered by asset class."""
    if asset_class is None:
        return list(SYMBOL_REGISTRY.keys())
    return [s for s, (c, _, _) in SYMBOL_REGISTRY.items() if c == asset_class]


def list_classes() -> List[str]:
    return ASSET_CLASSES.copy()


def get_price(symbol: str) -> float:
    """
    Current price for any supported symbol. Returns 0.0 on error.
    Cached for CACHE_TTL seconds.
    """
    symbol = symbol.upper()
    cached = _CACHE.get(symbol)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    asset_class, feed_sym, _ = get_symbol_info(symbol)
    if not asset_class:
        logger.warning(f"Unknown symbol: {symbol}")
        return 0.0

    try:
        if asset_class == "crypto":
            price = _fetch_crypto(feed_sym)
        else:
            price = _fetch_yfinance(feed_sym)
        if price > 0:
            _CACHE[symbol] = (price, time.time())
        return price
    except Exception as e:
        logger.error(f"feeds.get_price({symbol}): {e}")
        # Serve stale on error if we have any
        if cached:
            return cached[0]
        return 0.0


def get_prices(symbols: List[str]) -> Dict[str, float]:
    """Batch get prices for multiple symbols."""
    return {s: get_price(s) for s in symbols}


def _fetch_crypto(coingecko_id: str) -> float:
    """CoinGecko free tier: no key, ~50 calls/min."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    r = requests.get(url, params={"ids": coingecko_id, "vs_currencies": "usd"}, timeout=8)
    r.raise_for_status()
    data = r.json()
    return float(data.get(coingecko_id, {}).get("usd", 0) or 0)


def _fetch_yfinance(yf_symbol: str) -> float:
    """yfinance for non-crypto. Three fallbacks for off-hours reliability."""
    import yfinance as yf  # lazy import
    t = yf.Ticker(yf_symbol)

    # Path 1: fast_info.last_price (cheapest, sometimes None outside hours)
    try:
        p = t.fast_info.last_price
        if p and float(p) > 0:
            return float(p)
    except Exception:
        pass

    # Path 2: 5-day daily history → handles weekends/holidays
    try:
        hist = t.history(period="5d", interval="1d")
        if hist is not None and not hist.empty and "Close" in hist:
            p = float(hist["Close"].iloc[-1])
            if p > 0:
                return p
    except Exception as e:
        logger.debug(f"yf 5d failed for {yf_symbol}: {e}")

    # Path 3: 1-day intraday → freshest during market hours
    try:
        hist = t.history(period="1d", interval="5m")
        if hist is not None and not hist.empty:
            p = float(hist["Close"].iloc[-1])
            if p > 0:
                return p
    except Exception:
        pass

    return 0.0


def display_name(symbol: str) -> str:
    _, _, name = get_symbol_info(symbol)
    return name or symbol


def asset_class_of(symbol: str) -> Optional[str]:
    cls, _, _ = get_symbol_info(symbol)
    return cls


# Friendly emoji per asset class
CLASS_EMOJI = {
    "crypto":    "🔶",
    "stock":     "📈",
    "etf":       "📊",
    "forex":     "💱",
    "commodity": "🥇",
    "index":     "📉",
}

CLASS_LABEL = {
    "crypto":    "Crypto",
    "stock":     "Stocks",
    "etf":       "ETFs",
    "forex":     "Forex",
    "commodity": "Commodities",
    "index":     "Indexes",
}


# ─── Market hours detection ─────────────────────────────────────────────────
from datetime import timedelta

try:
    from zoneinfo import ZoneInfo
    _ET = ZoneInfo("America/New_York")
except ImportError:
    _ET = None  # fallback to fixed UTC-5 (no DST awareness)


def _now_et():
    if _ET:
        from datetime import datetime
        return datetime.now(_ET)
    from datetime import datetime, timezone
    return datetime.now(timezone(timedelta(hours=-5)))


def _next_us_equity_open(now):
    """Next NYSE open: 9:30 AM ET on next weekday."""
    candidate = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if now >= candidate:
        candidate += timedelta(days=1)
    while candidate.weekday() >= 5:  # skip Sat/Sun
        candidate += timedelta(days=1)
    return candidate


def _next_forex_open(now):
    """Forex opens Sun 5:00 PM ET."""
    days_until_sun = (6 - now.weekday()) % 7
    candidate = (now + timedelta(days=days_until_sun)).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


def get_market_status(asset_class: str) -> dict:
    """
    Returns {is_open: bool, market_name: str, opens_in_minutes: int, opens_at_str: str}
    """
    if asset_class == "crypto":
        return {"is_open": True, "market_name": "Crypto (24/7)",
                "opens_in_minutes": 0, "opens_at_str": "always open"}

    now = _now_et()

    # US equities: 9:30-16:00 ET, Mon-Fri
    if asset_class in ("stock", "etf", "index"):
        is_weekday = now.weekday() < 5
        open_t  = now.replace(hour=9,  minute=30, second=0, microsecond=0)
        close_t = now.replace(hour=16, minute=0,  second=0, microsecond=0)
        if is_weekday and open_t <= now < close_t:
            return {"is_open": True, "market_name": "US Stock Market",
                    "opens_in_minutes": 0, "opens_at_str": "open now"}
        nxt = _next_us_equity_open(now)
        delta_min = int((nxt - now).total_seconds() / 60)
        return {"is_open": False, "market_name": "US Stock Market",
                "opens_in_minutes": delta_min,
                "opens_at_str": nxt.strftime("%a %I:%M %p ET").lstrip("0")}

    # Forex: Sun 5pm ET → Fri 5pm ET
    if asset_class == "forex":
        wd, hr = now.weekday(), now.hour
        closed = (wd == 5) or (wd == 4 and hr >= 17) or (wd == 6 and hr < 17)
        if not closed:
            return {"is_open": True, "market_name": "Forex (24/5)",
                    "opens_in_minutes": 0, "opens_at_str": "open now"}
        nxt = _next_forex_open(now)
        delta_min = int((nxt - now).total_seconds() / 60)
        return {"is_open": False, "market_name": "Forex Market",
                "opens_in_minutes": delta_min,
                "opens_at_str": nxt.strftime("%a %I:%M %p ET").lstrip("0")}

    # Commodities (CME futures): like forex but with daily 5-6pm ET break
    if asset_class == "commodity":
        wd, hr = now.weekday(), now.hour
        weekend = (wd == 5) or (wd == 4 and hr >= 17) or (wd == 6 and hr < 18)
        daily_break = (wd < 5) and (hr == 17)
        if not (weekend or daily_break):
            return {"is_open": True, "market_name": "CME Futures",
                    "opens_in_minutes": 0, "opens_at_str": "open now"}
        if daily_break:
            nxt = now.replace(hour=18, minute=0, second=0, microsecond=0)
        else:
            nxt = _next_forex_open(now).replace(hour=18)
        delta_min = int((nxt - now).total_seconds() / 60)
        return {"is_open": False, "market_name": "CME Futures",
                "opens_in_minutes": delta_min,
                "opens_at_str": nxt.strftime("%a %I:%M %p ET").lstrip("0")}

    return {"is_open": True, "market_name": "Unknown",
            "opens_in_minutes": 0, "opens_at_str": ""}


def format_time_until(minutes: int) -> str:
    """Format minutes as 'X minutes' or 'Xh Ym'."""
    if minutes < 60:
        return f"{minutes} minutes"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h" if mins == 0 else f"{hours}h {mins}m"
