#!/usr/bin/env python3
"""
Binance API Client for OpenAsset Trading Bot
============================================

Wraps python-binance with hard safety guards:

  ✅ Symbol whitelist  — only BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
  ✅ Position cap      — $50 USD max per trade
  ✅ Min order check   — $10 USD min (Binance requirement)
  ✅ Withdraw guard    — refuses any key that has withdraw permission
  ✅ Price cache       — 15s TTL to avoid rate limits
  ✅ Defensive errors  — never crashes the calling bot

Credentials come from accounts.json per user, written by main.py's
existing API-key-linking flow.
"""

import os
import json
import time
import logging
from typing import Optional, Tuple, Dict

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

# ─── SAFETY LIMITS (hard-coded — change requires code review) ────────────────
MAX_USD_PER_TRADE = 50.0      # absolute cap, regardless of balance
MIN_USD_PER_TRADE = 10.0      # Binance minimum
RISK_PCT = 0.01               # 1% of USDT balance per trade
ALLOWED_SYMBOLS = {"BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"}

DB_PATH = "/root/openasset_club/telegram_bot/database"
CACHE_TTL = 15  # seconds

_PRICE_CACHE: Dict[str, Tuple[dict, float]] = {}


# ─── DB HELPERS ──────────────────────────────────────────────────────────────
def _load(name: str) -> dict:
    try:
        with open(f"{DB_PATH}/{name}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(name: str, data: dict) -> None:
    os.makedirs(DB_PATH, exist_ok=True)
    with open(f"{DB_PATH}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)


# ─── PER-USER STATE ──────────────────────────────────────────────────────────
def get_user_binance_creds(uid: str) -> Optional[Tuple[str, str]]:
    """Return (api_key, secret) or None if user hasn't linked Binance."""
    bn = _load("accounts").get(str(uid), {}).get("binance", {})
    if bn.get("api_key") and bn.get("secret_key"):
        return bn["api_key"], bn["secret_key"]
    return None


def is_live_mode(uid: str) -> bool:
    """True if user has explicitly opted into live trading. Default: False."""
    bn = _load("accounts").get(str(uid), {}).get("binance", {})
    return bn.get("live_mode", False) is True


def set_live_mode(uid: str, live: bool) -> None:
    accounts = _load("accounts")
    accounts.setdefault(str(uid), {}).setdefault("binance", {})["live_mode"] = bool(live)
    _save("accounts", accounts)


def to_binance_symbol(sym: str) -> str:
    """Normalize dashboard symbols → Binance symbols (BTCUSD → BTCUSDT)."""
    if sym.endswith("USD") and not sym.endswith("USDT"):
        return sym + "T"
    return sym


# ─── BINANCE CLIENT WRAPPER ──────────────────────────────────────────────────
class BinanceClient:
    """Safety-wrapped Binance Spot API client."""

    def __init__(self, api_key: str, secret_key: str):
        if not BINANCE_AVAILABLE:
            raise RuntimeError("python-binance not installed")
        self.client = Client(api_key, secret_key)

    # ── Verification ────────────────────────────────────────────────────────
    def verify_credentials(self) -> Tuple[bool, str]:
        """
        Check the API key works AND does NOT have withdraw permission.
        Returns (ok, human_message).
        """
        try:
            self.client.get_account()  # fails immediately on bad creds
            perms = self.client.get_account_api_permissions()
        except BinanceAPIException as e:
            return False, f"❌ Binance error: {e.message}"
        except Exception as e:
            return False, f"❌ Connection error: {e}"

        if perms.get("enableWithdrawals"):
            return False, (
                "⛔ *DANGER*: This API key has WITHDRAW permission.\n\n"
                "Regenerate the key on Binance with ONLY:\n"
                "  ✅ Enable Reading\n"
                "  ✅ Enable Spot Trading\n"
                "  ❌ Enable Withdrawals (UNCHECK)\n\n"
                "Trading is BLOCKED until you fix this."
            )
        if not perms.get("enableSpotAndMarginTrading"):
            return False, "❌ API key cannot trade. Enable Spot Trading."
        return True, "✅ API key verified — read + trade only (no withdraw)."

    # ── Read ────────────────────────────────────────────────────────────────
    def get_balance(self, asset: str = "USDT") -> float:
        try:
            bal = self.client.get_asset_balance(asset=asset)
            return float(bal["free"]) if bal else 0.0
        except Exception as e:
            logger.error(f"get_balance({asset}): {e}")
            return 0.0

    def get_all_balances(self) -> Dict[str, float]:
        try:
            return {
                b["asset"]: float(b["free"])
                for b in self.client.get_account()["balances"]
                if float(b["free"]) > 0
            }
        except Exception as e:
            logger.error(f"get_all_balances: {e}")
            return {}

    def get_price(self, symbol: str) -> float:
        symbol = to_binance_symbol(symbol)
        cached = _PRICE_CACHE.get(f"p_{symbol}")
        if cached and time.time() - cached[1] < CACHE_TTL:
            return cached[0]["price"]
        try:
            price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])
            _PRICE_CACHE[f"p_{symbol}"] = ({"price": price}, time.time())
            return price
        except Exception as e:
            logger.error(f"get_price({symbol}): {e}")
            return 0.0

    def get_24h_stats(self, symbol: str) -> dict:
        symbol = to_binance_symbol(symbol)
        cached = _PRICE_CACHE.get(f"s_{symbol}")
        if cached and time.time() - cached[1] < CACHE_TTL:
            return cached[0]
        try:
            s = self.client.get_ticker(symbol=symbol)
            stats = {
                "price":      float(s["lastPrice"]),
                "high":       float(s["highPrice"]),
                "low":        float(s["lowPrice"]),
                "change_pct": float(s["priceChangePercent"]),
            }
            _PRICE_CACHE[f"s_{symbol}"] = (stats, time.time())
            return stats
        except Exception as e:
            logger.error(f"get_24h_stats({symbol}): {e}")
            return {"price": 0, "high": 0, "low": 0, "change_pct": 0}

    # ── Write (places real orders) ──────────────────────────────────────────
    def place_market_buy(self, symbol: str, usd_amount: float) -> dict:
        """
        Place a MARKET BUY order. Returns:
          { success: True,  order_id, fill_price, qty, symbol }
          { success: False, error: "..." }
        """
        symbol = to_binance_symbol(symbol)
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"Symbol {symbol} not whitelisted"}
        if usd_amount > MAX_USD_PER_TRADE:
            return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
        if usd_amount < MIN_USD_PER_TRADE:
            return {"success": False, "error": f"Min order is ${MIN_USD_PER_TRADE}"}
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quoteOrderQty=round(usd_amount, 2),
            )
            fills = order.get("fills", [])
            qty = sum(float(f["qty"]) for f in fills)
            avg = (
                sum(float(f["price"]) * float(f["qty"]) for f in fills) / qty
                if qty else 0.0
            )
            return {
                "success":    True,
                "order_id":   order["orderId"],
                "symbol":     symbol,
                "fill_price": avg,
                "qty":        qty,
                "usd_spent":  usd_amount,
            }
        except BinanceAPIException as e:
            logger.error(f"market_buy({symbol}, ${usd_amount}): {e}")
            return {"success": False, "error": e.message}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def place_market_sell(self, symbol: str, qty: float) -> dict:
        symbol = to_binance_symbol(symbol)
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"Symbol {symbol} not whitelisted"}
        try:
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=round(qty, 6),
            )
            fills = order.get("fills", [])
            avg = (
                sum(float(f["price"]) * float(f["qty"]) for f in fills)
                / sum(float(f["qty"]) for f in fills)
                if fills else 0.0
            )
            return {
                "success":    True,
                "order_id":   order["orderId"],
                "symbol":     symbol,
                "fill_price": avg,
                "qty":        qty,
            }
        except BinanceAPIException as e:
            return {"success": False, "error": e.message}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def place_market_buy_with_sl_tp(self, symbol: str, usd_amount: float,
                                      sl_pct: float = 0.5, tp_pct: float = 3.0) -> dict:
        """
        Place market BUY with automatic SL/TP using OCO (One-Cancels-Other) order.
        
        Flow:
          1. Place market BUY
          2. Calculate SL price (entry * (1 - sl_pct/100))
          3. Calculate TP price (entry * (1 + tp_pct/100))
          4. Place OCO: SELL at SL or TP (whichever hits first)
        
        Returns:
          {
            "success": True,
            "buy_order_id": int,
            "oco_order_id": int,
            "symbol": str,
            "qty": float,
            "entry_price": float,
            "sl_price": float,
            "tp_price": float,
            "sl_pct": float,
            "tp_pct": float
          }
          OR
          {
            "success": False,
            "error": str,
            "buy_order_id": int (if buy succeeded but OCO failed)
          }
        """
        symbol = to_binance_symbol(symbol)
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"Symbol {symbol} not whitelisted"}
        if usd_amount > MAX_USD_PER_TRADE:
            return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
        if usd_amount < MIN_USD_PER_TRADE:
            return {"success": False, "error": f"Min order is ${MIN_USD_PER_TRADE}"}

        buy_order_id = None
        try:
            # 1. Place market BUY
            buy_order = self.client.order_market_buy(
                symbol=symbol,
                quoteOrderQty=round(usd_amount, 2),
            )
            buy_order_id = buy_order["orderId"]
            
            # Get actual fill price and quantity
            fills = buy_order.get("fills", [])
            qty = sum(float(f["qty"]) for f in fills)
            entry_price = (
                sum(float(f["price"]) * float(f["qty"]) for f in fills) / qty
                if qty else 0.0
            )
            
            # 2. Calculate SL/TP prices
            sl_price = entry_price * (1 - sl_pct / 100)
            tp_price = entry_price * (1 + tp_pct / 100)
            
            # Round to 8 decimals (Binance standard)
            sl_price = round(sl_price, 8)
            tp_price = round(tp_price, 8)
            qty_sell = round(qty, 8)
            
            # 3. Place OCO order (SELL at SL or TP)
            try:
                oco_order = self.client.create_oco_order(
                    symbol=symbol,
                    side="SELL",
                    quantity=qty_sell,
                    price=tp_price,              # Limit price for TP (sell at this or better)
                    stopPrice=sl_price,          # Stop price for SL
                    stopLimitPrice=round(sl_price * 0.999, 8),  # Slightly below to ensure fill
                    stopLimitTimeInForce="GTC",
                )
                oco_order_id = oco_order.get("orderListId")
                
                logger.info(f"SL/TP: {symbol} BUY @ ${entry_price:.2f} qty={qty}, "
                           f"SL=${sl_price:.2f}, TP=${tp_price:.2f}")
                
                return {
                    "success": True,
                    "buy_order_id": buy_order_id,
                    "oco_order_id": oco_order_id,
                    "symbol": symbol,
                    "qty": qty,
                    "entry_price": entry_price,
                    "sl_price": sl_price,
                    "tp_price": tp_price,
                    "sl_pct": sl_pct,
                    "tp_pct": tp_pct,
                }
            except BinanceAPIException as oco_err:
                # BUY succeeded but OCO failed — warn but return partial success
                logger.error(f"OCO failed for {symbol} (buy succeeded): {oco_err.message}")
                return {
                    "success": False,
                    "error": f"OCO failed: {oco_err.message}. Buy succeeded (order {buy_order_id}), but no SL/TP. MANUAL CONTROL REQUIRED.",
                    "buy_order_id": buy_order_id,
                }
        except BinanceAPIException as e:
            logger.error(f"market_buy_with_sl_tp({symbol}): {e.message}")
            return {"success": False, "error": e.message}
        except Exception as e:
            logger.error(f"market_buy_with_sl_tp({symbol}): {str(e)}")
            return {"success": False, "error": str(e)}


# ─── CONVENIENCE FACTORY ─────────────────────────────────────────────────────
def get_client_for_user(uid: str) -> Optional[BinanceClient]:
    """Return a connected BinanceClient for user, or None."""
    creds = get_user_binance_creds(uid)
    if not creds:
        return None
    try:
        return BinanceClient(*creds)
    except Exception as e:
        logger.error(f"BinanceClient init failed for {uid}: {e}")
        return None


def calc_trade_size_usd(usdt_balance: float) -> float:
    """1% of balance, capped at MAX_USD_PER_TRADE, never below MIN."""
    raw = usdt_balance * RISK_PCT
    return max(MIN_USD_PER_TRADE, min(raw, MAX_USD_PER_TRADE))
