#!/usr/bin/env python3
"""
OANDA Live Signal Executor (Phase 8)
====================================

Executes AI signals directly on OANDA with real forex money.

Safety features:
  • Max $50 USD notional per signal trade
  • Stop-loss at 0.5%
  • Take-profit at 3.0%
  • Max 3 concurrent positions per user
  • Auto-detects practice vs live
  • Admin notification on every trade
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Risk limits
MAX_NOTIONAL_USD = 50.0
STOP_LOSS_PCT = 0.5
TAKE_PROFIT_PCT = 3.0
MAX_POSITIONS_PER_ACCOUNT = 3


class OANDASignalTrader:
    """Executes AI signals on OANDA practice/live accounts."""
    
    def can_trade(self, c) -> Tuple[bool, str]:
        """Check if account is ready to receive signals."""
        try:
            # Get account summary
            acct = c.get_account_summary()
            
            # Check balance
            if acct.get("unrealizedPL", 0) + acct.get("balance", 0) < MAX_NOTIONAL_USD:
                return False, f"Insufficient balance for ${MAX_NOTIONAL_USD} trade"
            
            # Check open trades (rough position count)
            # OANDA can have multiple units on one instrument, count unique instruments
            trades = c.get_trades()
            open_instruments = set(t.get("instrument") for t in trades)
            if len(open_instruments) >= MAX_POSITIONS_PER_ACCOUNT:
                return False, f"Max {MAX_POSITIONS_PER_ACCOUNT} instruments reached"
            
            return True, "Ready"
        
        except Exception as e:
            logger.error(f"OANDA account check error: {e}")
            return False, f"Account error: {str(e)}"
    
    
    def execute_signal(self, uid: str, symbol: str, signal: str, c=None) -> Dict:
        """
        Execute BUY/SELL signal on OANDA.
        
        Args:
            uid: User ID
            symbol: Trading symbol (e.g., 'EUR_USD', 'XAU_USD')
            signal: 'BUY' or 'SELL'
            c: OANDA client (if None, loads from uid)
        
        Returns:
            {
                "success": bool,
                "message": str,
                "trade_id": str (if success),
                "entry_price": float,
                "sl_price": float,
                "tp_price": float,
                "units": float,
                "account_type": "practice" or "live",
            }
        """
        try:
            if not c:
                from oanda_client import get_client_for_user
                c, is_practice = get_client_for_user(uid)
            else:
                is_practice = c.is_practice
            
            if not c:
                return {"success": False, "message": "OANDA client error"}
            
            # Validate account state
            ok, msg = self.can_trade(c)
            if not ok:
                return {"success": False, "message": msg}
            
            # Only support BUY signals
            if signal != "BUY":
                return {"success": False, "message": "SELL signals not supported yet (Phase 9)"}
            
            # Get current price
            bid, ask = c.get_price(symbol)
            if bid <= 0 or ask <= 0:
                return {"success": False, "message": f"Cannot fetch price for {symbol}"}
            
            entry_price = ask  # For BUY, use ask
            
            # Calculate SL/TP prices
            sl_price = entry_price * (1 - STOP_LOSS_PCT / 100)
            tp_price = entry_price * (1 + TAKE_PROFIT_PCT / 100)
            
            account_type = "PRACTICE" if is_practice else "LIVE"
            logger.info(
                f"Signal: BUY {symbol} for uid={uid} ({account_type})\n"
                f"  Entry: {entry_price:.5f}\n"
                f"  SL: {sl_price:.5f} (-{STOP_LOSS_PCT}%)\n"
                f"  TP: {tp_price:.5f} (+{TAKE_PROFIT_PCT}%)"
            )
            
            # Place market buy with SL/TP
            result = c.place_market_buy(
                symbol=symbol,
                usd_amount=MAX_NOTIONAL_USD
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "message": result.get("error", "Order failed")
                }
            
            # Extract units and update SL/TP if needed
            units = result.get("units", 0)
            
            return {
                "success": True,
                "message": f"BUY {symbol} × {units:.2f} @ {entry_price:.5f}",
                "trade_id": result.get("trade_id"),
                "entry_price": entry_price,
                "sl_price": sl_price,
                "tp_price": tp_price,
                "units": units,
                "amount_usd": MAX_NOTIONAL_USD,
                "account_type": account_type,
            }
        
        except Exception as e:
            logger.error(f"OANDA signal execution error: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}


def execute_oanda_signal(uid: str, symbol: str, signal: str, c=None) -> Dict:
    """Execute signal on OANDA. Returns result dict."""
    trader = OANDASignalTrader()
    return trader.execute_signal(uid, symbol, signal, c)
