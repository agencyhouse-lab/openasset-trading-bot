#!/usr/bin/env python3
"""
OANDA REST API Client — Forex, Metals, Indices
===============================================

Covers 20+ instruments across forex, metals, and indices.
Supports both OANDA Practice (free demo) and Live accounts.

User setup:
  1. Create free account at oanda.com
  2. Go to Manage Funds → API Access → Generate token
  3. Note your account ID (format: 001-001-XXXXXXX-001)
  4. Add both to OpenAsset bot (Trading Menu → OANDA)

Auth: Bearer token in Authorization header.
Practice API: https://api-fxpractice.oanda.com/v3
Live API:      https://api-fxtrade.oanda.com/v3
"""

import json
import logging
import time
from typing import Optional, Dict, Tuple

import requests

logger = logging.getLogger(__name__)

# ─── Endpoints ──────────────────────────────────────────────────────────────
PRACTICE_URL = "https://api-fxpractice.oanda.com/v3"
LIVE_URL = "https://api-fxtrade.oanda.com/v3"
TIMEOUT = 10  # seconds
MAX_USD_PER_TRADE = 200.0  # forex needs bigger size than equities ($50 too small)
MIN_USD_PER_TRADE = 10.0

DB_PATH = "/root/openasset_club/telegram_bot/database"

# ─── Supported instruments (OANDA format: BASE_QUOTE) ────────────────────────
INSTRUMENTS: Dict[str, str] = {
    # Forex majors
    "EURUSD": "EUR_USD",
    "GBPUSD": "GBP_USD",
    "USDJPY": "USD_JPY",
    "AUDUSD": "AUD_USD",
    "USDCHF": "USD_CHF",
    "USDCAD": "USD_CAD",
    "NZDUSD": "NZD_USD",
    # Forex minors
    "EURGBP": "EUR_GBP",
    "EURJPY": "EUR_JPY",
    "GBPJPY": "GBP_JPY",
    "AUDJPY": "AUD_JPY",
    # Metals
    "XAUUSD": "XAU_USD",   # Gold
    "XAGUSD": "XAG_USD",   # Silver
    # Indices (CFD)
    "US30":   "US30_USD",  # Dow Jones
    "SPX500": "SPX500_USD",
    "NAS100": "NAS100_USD",
    "UK100":  "UK100_GBP",
    "GER40":  "DE40_EUR",  # DAX
    # Oil
    "BRENT":  "BCO_USD",
    "WTI":    "WTICO_USD",
}

INSTRUMENT_DISPLAY = {
    "EURUSD": "EUR/USD",  "GBPUSD": "GBP/USD",  "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",  "USDCHF": "USD/CHF",  "USDCAD": "USD/CAD",
    "NZDUSD": "NZD/USD",  "EURGBP": "EUR/GBP",  "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY",  "AUDJPY": "AUD/JPY",  "XAUUSD": "Gold",
    "XAGUSD": "Silver",   "US30":   "Dow Jones", "SPX500": "S&P 500",
    "NAS100": "Nasdaq",   "UK100":  "FTSE 100",  "GER40":  "DAX 40",
    "BRENT":  "Brent Oil","WTI":    "WTI Oil",
}

INSTRUMENT_GROUPS = {
    "forex_major":  ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD"],
    "forex_minor":  ["EURGBP", "EURJPY", "GBPJPY", "AUDJPY"],
    "metals":       ["XAUUSD", "XAGUSD"],
    "indices":      ["US30", "SPX500", "NAS100", "UK100", "GER40"],
    "energy":       ["BRENT", "WTI"],
}

_PRICE_CACHE: Dict[str, Tuple[float, float]] = {}
CACHE_TTL = 15


# ─── DB helpers ──────────────────────────────────────────────────────────────
def _load(name):
    try:
        with open(f"{DB_PATH}/{name}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_user_oanda_creds(uid: str) -> Optional[Tuple[str, str]]:
    """Return (token, account_id) or None."""
    d = _load("accounts").get(str(uid), {}).get("oanda", {})
    if d.get("token") and d.get("account_id"):
        return d["token"], d["account_id"]
    return None


# ─── Client ──────────────────────────────────────────────────────────────────
class OandaClient:
    def __init__(self, token: str, account_id: str, practice: bool = True):
        self.account_id = account_id
        self.practice = practice
        self.base = PRACTICE_URL if practice else LIVE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def _get(self, path: str, **params) -> dict:
        r = self.session.get(f"{self.base}{path}", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        r = self.session.post(f"{self.base}{path}", json=body, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    def verify(self) -> Tuple[bool, str]:
        try:
            data = self._get(f"/accounts/{self.account_id}/summary")
            a = data["account"]
            bal = float(a.get("balance", 0))
            currency = a.get("currency", "USD")
            env = "PRACTICE" if self.practice else "LIVE"
            return True, (f"✅ OANDA {env} connected.\n"
                         f"Balance: {currency} {bal:,.2f}")
        except Exception as e:
            return False, f"❌ OANDA error: {e}"

    def get_balance(self) -> float:
        try:
            data = self._get(f"/accounts/{self.account_id}/summary")
            return float(data["account"]["balance"])
        except Exception:
            return 0.0

    def get_nav(self) -> float:
        """Net Asset Value including open positions."""
        try:
            data = self._get(f"/accounts/{self.account_id}/summary")
            return float(data["account"]["NAV"])
        except Exception:
            return 0.0

    def get_price(self, symbol: str) -> Tuple[float, float]:
        """Return (bid, ask). Returns (0, 0) on error."""
        symbol = symbol.upper()
        cached = _PRICE_CACHE.get(symbol)
        if cached and time.time() - cached[1] < CACHE_TTL:
            return cached[0], cached[0]  # returns mid for simplicity

        oanda_sym = INSTRUMENTS.get(symbol)
        if not oanda_sym:
            return 0.0, 0.0
        try:
            data = self._get(
                f"/accounts/{self.account_id}/pricing",
                instruments=oanda_sym,
            )
            price_data = data["prices"][0]
            bid = float(price_data["bids"][0]["price"])
            ask = float(price_data["asks"][0]["price"])
            mid = (bid + ask) / 2
            _PRICE_CACHE[symbol] = (mid, time.time())
            return bid, ask
        except Exception as e:
            logger.error(f"oanda get_price({symbol}): {e}")
            return 0.0, 0.0

    def get_mid_price(self, symbol: str) -> float:
        bid, ask = self.get_price(symbol)
        return (bid + ask) / 2 if ask > 0 else 0.0

    def get_open_positions(self) -> list:
        try:
            data = self._get(f"/accounts/{self.account_id}/openPositions")
            return data.get("positions", [])
        except Exception:
            return []

    def place_market_buy(self, symbol: str, usd_amount: float) -> dict:
        """Buy notional USD worth of symbol."""
        symbol = symbol.upper()
        oanda_sym = INSTRUMENTS.get(symbol)
        if not oanda_sym:
            return {"success": False, "error": f"{symbol} not supported"}
        if usd_amount > MAX_USD_PER_TRADE:
            return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
        if usd_amount < MIN_USD_PER_TRADE:
            return {"success": False, "error": f"Min ${MIN_USD_PER_TRADE}"}

        _, ask = self.get_price(symbol)
        if ask <= 0:
            return {"success": False, "error": f"Price unavailable for {symbol}"}

        # Convert USD notional to units
        units = int(usd_amount / ask)
        if units < 1:
            return {"success": False, "error": f"Calculated units < 1 (try larger amount)"}

        try:
            body = {"order": {
                "type": "MARKET",
                "instrument": oanda_sym,
                "units": str(units),
                "timeInForce": "FOK",
            }}
            data = self._post(f"/accounts/{self.account_id}/orders", body)
            fill = data.get("orderFillTransaction", {})
            fill_price = float(fill.get("price", ask))
            trade_id = fill.get("tradeOpened", {}).get("tradeID", "")
            return {
                "success": True,
                "order_id": fill.get("id", ""),
                "trade_id": trade_id,
                "symbol": symbol,
                "units": units,
                "fill_price": fill_price,
                "usd_spent": units * fill_price,
            }
        except Exception as e:
            logger.error(f"oanda buy({symbol}): {e}")
            return {"success": False, "error": str(e)}

    def close_trade(self, symbol: str) -> dict:
        """Close all units of the given instrument."""
        symbol = symbol.upper()
        oanda_sym = INSTRUMENTS.get(symbol)
        if not oanda_sym:
            return {"success": False, "error": f"{symbol} not supported"}
        try:
            # Close long position
            r = self.session.put(
                f"{self.base}/accounts/{self.account_id}/positions/{oanda_sym}/close",
                json={"longUnits": "ALL"},
                timeout=TIMEOUT,
            )
            if r.status_code == 200:
                return {"success": True, "symbol": symbol}
            elif r.status_code == 404:
                return {"success": False, "error": f"No open {symbol} position"}
            r.raise_for_status()
            return {"success": True, "symbol": symbol}
        except Exception as e:
            logger.error(f"oanda close({symbol}): {e}")
            return {"success": False, "error": str(e)}


# ─── Factory ─────────────────────────────────────────────────────────────────
def make_oanda_client(token: str, account_id: str):
    """Auto-detect practice vs live from account ID, then verify."""
    # Practice accounts typically contain '-001-' in ID or start with '001'
    # Live accounts typically start with '001' too — just try practice first
    for practice in (True, False):
        try:
            c = OandaClient(token, account_id, practice=practice)
            ok, msg = c.verify()
            if ok:
                return c, practice
        except Exception:
            continue
    return None, None


def get_client_for_user(uid: str):
    """Return (OandaClient, is_practice) or (None, None)."""
    creds = get_user_oanda_creds(uid)
    if not creds:
        return None, None
    return make_oanda_client(*creds)


def has_oanda(uid: str) -> bool:
    return get_user_oanda_creds(uid) is not None
