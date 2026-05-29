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
    """yfinance for everything non-crypto. Uses fast_info to avoid heavy queries."""
    import yfinance as yf  # lazy import — only when needed
    t = yf.Ticker(yf_symbol)
    # fast_info is the lightweight path
    try:
        price = t.fast_info.last_price
        if price and price > 0:
            return float(price)
    except Exception:
        pass
    # Fallback: 1-day history
    hist = t.history(period="1d", interval="1m")
    if not hist.empty:
        return float(hist["Close"].iloc[-1])
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
