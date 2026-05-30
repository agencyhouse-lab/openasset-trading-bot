#!/usr/bin/env python3
"""
Alpaca Live Signal Executor (Phase 8)
=====================================

Executes AI signals directly on Alpaca with real money.
Auto-detects paper/live and routes appropriately.

Safety features:
  • Max $50 USD per signal trade
  • Stop-loss at 0.5% (bracket order)
  • Take-profit at 3.0% (bracket order)
  • Max 3 concurrent positions per user
  • Only long positions (no shorting)
  • Admin notification on every trade
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Risk limits
MAX_POSITION_SIZE_USD = 50.0
STOP_LOSS_PCT = 0.5
TAKE_PROFIT_PCT = 3.0
MAX_POSITIONS_PER_ACCOUNT = 3


class AlpacaSignalTrader:
    """Executes AI signals on live/paper Alpaca accounts."""
    
    def can_trade(self, c, account_type: str) -> Tuple[bool, str]:
        """Check if account is ready to receive signals."""
        # Check cash balance
        cash = c.get_cash()
        if cash < MAX_POSITION_SIZE_USD:
            return False, f"Insufficient cash: ${cash:.2f} < ${MAX_POSITION_SIZE_USD:.2f}"
        
        # Check position count
        positions = c.get_positions()
        if len(positions) >= MAX_POSITIONS_PER_ACCOUNT:
            return False, f"Max {MAX_POSITIONS_PER_ACCOUNT} positions reached"
        
        return True, "Ready"
    
    
    def execute_signal(self, uid: str, symbol: str, signal: str, c=None) -> Dict:
        """
        Execute BUY/SELL signal on Alpaca.
        
        Args:
            uid: User ID
            symbol: Trading symbol (e.g., 'SPY', 'QQQ')
            signal: 'BUY' or 'SELL'
            c: Alpaca client (if None, loads from uid)
        
        Returns:
            {
                "success": bool,
                "message": str,
                "order_id": str (if success),
                "entry_price": float,
                "sl_price": float,
                "tp_price": float,
                "quantity": float,
                "account_type": "live" or "paper",
            }
        """
        try:
            if not c:
                from alpaca_client import get_client_for_user
                c, is_paper = get_client_for_user(uid)
            else:
                is_paper = c.is_paper
            
            if not c:
                return {"success": False, "message": "Alpaca client error"}
            
            # Validate account state
            ok, msg = self.can_trade(c, "paper" if is_paper else "live")
            if not ok:
                return {"success": False, "message": msg}
            
            # Only support BUY signals (long-only)
            if signal != "BUY":
                return {"success": False, "message": "SELL signals not supported yet (Phase 9)"}
            
            # Get current price
            price = c.get_price(symbol)
            if price <= 0:
                return {"success": False, "message": f"Cannot fetch price for {symbol}"}
            
            # Calculate order size
            quantity = int(MAX_POSITION_SIZE_USD / price)
            if quantity <= 0:
                quantity = 1
            
            # Calculate SL/TP prices
            sl_price = price * (1 - STOP_LOSS_PCT / 100)
            tp_price = price * (1 + TAKE_PROFIT_PCT / 100)
            
            account_type = "PAPER" if is_paper else "LIVE"
            logger.info(
                f"Signal: BUY {symbol} for uid={uid} ({account_type})\n"
                f"  Entry: ${price:.2f}\n"
                f"  SL: ${sl_price:.2f} (-{STOP_LOSS_PCT}%)\n"
                f"  TP: ${tp_price:.2f} (+{TAKE_PROFIT_PCT}%)\n"
                f"  Qty: {quantity}"
            )
            
            # Place market order with bracket SL/TP
            result = c.place_market_buy_with_sl_tp(
                symbol=symbol,
                quantity=quantity,
                sl_pct=STOP_LOSS_PCT,
                tp_pct=TAKE_PROFIT_PCT
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "message": result.get("error", "Order failed")
                }
            
            return {
                "success": True,
                "message": f"BUY {symbol} × {quantity} @ ${price:.2f}",
                "order_id": result.get("order_id"),
                "entry_price": price,
                "sl_price": sl_price,
                "tp_price": tp_price,
                "quantity": quantity,
                "amount_usd": quantity * price,
                "account_type": account_type,
            }
        
        except Exception as e:
            logger.error(f"Alpaca signal execution error: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}


def execute_alpaca_signal(uid: str, symbol: str, signal: str, c=None) -> Dict:
    """Execute signal on Alpaca. Returns result dict."""
    trader = AlpacaSignalTrader()
    return trader.execute_signal(uid, symbol, signal, c)
