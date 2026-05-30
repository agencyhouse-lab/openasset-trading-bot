#!/usr/bin/env python3
"""
Alpaca API Client for OpenAsset Trading Bot
===========================================

Stocks / ETFs trading with safety guards. Auto-detects whether the
user's keys are PAPER or LIVE and connects to the right endpoint.

  ✅ Symbol whitelist  — common liquid ETFs/stocks
  ✅ Position cap       — $50 USD max per trade
  ✅ Fractional orders  — uses notional (dollar) amounts
  ✅ Defensive errors   — never crashes the caller

Alpaca PAPER accounts use fake money — ideal for testing with zero risk.
"""

import json
import time
import logging
from typing import Optional, Tuple, Dict

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestTradeRequest
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

logger = logging.getLogger(__name__)

MAX_USD_PER_TRADE = 50.0
MIN_USD_PER_TRADE = 1.0
ALLOWED_SYMBOLS = {"SPY", "QQQ", "GLD", "USO", "IWM", "DIA",
                   "AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"}
DB_PATH = "/root/openasset_club/telegram_bot/database"
CACHE_TTL = 15
_PRICE_CACHE: Dict[str, Tuple[float, float]] = {}


def _load(name):
    try:
        with open(f"{DB_PATH}/{name}.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_user_alpaca_creds(uid: str) -> Optional[Tuple[str, str]]:
    al = _load("accounts").get(str(uid), {}).get("alpaca", {})
    if al.get("api_key") and al.get("secret_key"):
        return al["api_key"], al["secret_key"]
    return None


class AlpacaClient:
    def __init__(self, api_key, secret_key, paper=True):
        if not ALPACA_AVAILABLE:
            raise RuntimeError("alpaca-py not installed")
        self.paper = paper
        self.trading = TradingClient(api_key, secret_key, paper=paper)
        self.data = StockHistoricalDataClient(api_key, secret_key)

    def verify_credentials(self) -> Tuple[bool, str]:
        try:
            acct = self.trading.get_account()
            kind = "PAPER" if self.paper else "LIVE"
            return True, (
                f"✅ Alpaca connected ({kind}).\n"
                f"Buying power: ${float(acct.buying_power):,.2f}"
            )
        except Exception as e:
            return False, f"❌ Alpaca error: {e}"

    def get_cash(self) -> float:
        try:
            return float(self.trading.get_account().cash)
        except Exception as e:
            logger.error(f"alpaca get_cash: {e}")
            return 0.0

    def get_portfolio_value(self) -> float:
        try:
            return float(self.trading.get_account().portfolio_value)
        except Exception:
            return 0.0

    def get_price(self, symbol: str) -> float:
        cached = _PRICE_CACHE.get(symbol)
        if cached and time.time() - cached[1] < CACHE_TTL:
            return cached[0]
        try:
            req = StockLatestTradeRequest(symbol_or_symbols=symbol)
            latest = self.data.get_stock_latest_trade(req)
            price = float(latest[symbol].price)
            _PRICE_CACHE[symbol] = (price, time.time())
            return price
        except Exception as e:
            logger.error(f"alpaca get_price({symbol}): {e}")
            return 0.0

    def place_market_buy(self, symbol: str, usd_amount: float) -> dict:
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"{symbol} not whitelisted"}
        if usd_amount > MAX_USD_PER_TRADE:
            return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
        if usd_amount < MIN_USD_PER_TRADE:
            return {"success": False, "error": f"Min order ${MIN_USD_PER_TRADE}"}
        try:
            req = MarketOrderRequest(
                symbol=symbol,
                notional=round(usd_amount, 2),
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
            order = self.trading.submit_order(req)
            price = self.get_price(symbol)
            return {
                "success":    True,
                "order_id":   str(order.id),
                "symbol":     symbol,
                "usd_spent":  usd_amount,
                "fill_price": price,
                "qty":        (usd_amount / price) if price else 0,
            }
        except Exception as e:
            logger.error(f"alpaca buy({symbol}, ${usd_amount}): {e}")
            return {"success": False, "error": str(e)}

    def place_market_sell(self, symbol: str) -> dict:
        """Close the entire position in this symbol."""
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"{symbol} not whitelisted"}
        try:
            order = self.trading.close_position(symbol)
            return {
                "success":  True,
                "order_id": str(order.id) if hasattr(order, "id") else "closed",
                "symbol":   symbol,
                "fill_price": self.get_price(symbol),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def place_market_buy_with_sl_tp(self, symbol: str, usd_amount: float,
                                     sl_pct: float = 0.5, tp_pct: float = 3.0) -> dict:
        """
        Place market BUY with automatic SL/TP using Alpaca bracket orders.
        
        Alpaca's bracket orders automatically create protective orders:
          - take_profit: sell at this price (TP)
          - stop_loss: sell at this price (SL)
        
        When either is hit, the other is automatically cancelled.
        
        Returns:
          {
            "success": True,
            "buy_order_id": str,
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
            "error": str
          }
        """
        if symbol not in ALLOWED_SYMBOLS:
            return {"success": False, "error": f"{symbol} not whitelisted"}
        if usd_amount > MAX_USD_PER_TRADE:
            return {"success": False, "error": f"${usd_amount:.2f} exceeds ${MAX_USD_PER_TRADE} cap"}
        if usd_amount < MIN_USD_PER_TRADE:
            return {"success": False, "error": f"Min order ${MIN_USD_PER_TRADE}"}

        try:
            # Get current price to calculate qty and SL/TP
            entry_price = self.get_price(symbol)
            if not entry_price or entry_price <= 0:
                return {"success": False, "error": f"Cannot get price for {symbol}"}
            
            qty = round(usd_amount / entry_price, 2)
            
            # Calculate SL/TP prices
            sl_price = round(entry_price * (1 - sl_pct / 100), 2)
            tp_price = round(entry_price * (1 + tp_pct / 100), 2)
            
            # Create bracket order with take_profit and stop_loss
            # Alpaca will automatically create the protective orders
            from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
            
            req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                take_profit=TakeProfitRequest(limit_price=tp_price),
                stop_loss=StopLossRequest(stop_price=sl_price),
            )
            
            order = self.trading.submit_order(req)
            
            logger.info(f"SL/TP: {symbol} BUY @ ${entry_price} qty={qty}, "
                       f"SL=${sl_price}, TP=${tp_price}")
            
            return {
                "success": True,
                "buy_order_id": str(order.id),
                "symbol": symbol,
                "qty": qty,
                "entry_price": entry_price,
                "sl_price": sl_price,
                "tp_price": tp_price,
                "sl_pct": sl_pct,
                "tp_pct": tp_pct,
            }
        except Exception as e:
            logger.error(f"alpaca buy_with_sl_tp({symbol}): {e}")
            return {"success": False, "error": str(e)}


def make_alpaca_client(api_key, secret_key):
    """
    Auto-detect paper vs live. Tries paper first (safer), then live.
    Returns (AlpacaClient, is_paper) or (None, None).
    """
    if not ALPACA_AVAILABLE:
        return None, None
    for paper in (True, False):
        try:
            c = AlpacaClient(api_key, secret_key, paper=paper)
            c.trading.get_account()  # validate
            return c, paper
        except Exception:
            continue
    return None, None


def get_client_for_user(uid: str):
    """Return (AlpacaClient, is_paper) for user, or (None, None)."""
    creds = get_user_alpaca_creds(uid)
    if not creds:
        return None, None
    return make_alpaca_client(*creds)


def calc_trade_size_usd(buying_power: float) -> float:
    raw = buying_power * 0.01
    return max(MIN_USD_PER_TRADE, min(raw, MAX_USD_PER_TRADE))
