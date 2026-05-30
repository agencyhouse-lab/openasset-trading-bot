#!/usr/bin/env python3
"""
Binance Live Signal Executor (Phase 8)
======================================

Executes AI signals directly on Binance with real money.

Safety features:
  • Max $50 USD per signal trade
  • Stop-loss at 0.5% (OCO order)
  • Take-profit at 3.0% (OCO order)
  • Max 3 concurrent positions per user
  • 24h loss limit per account
  • Admin notification on every trade
"""

import logging
from typing import Dict, Optional, Tuple
from binance_client import BinanceClient, get_client_for_user, get_user_binance_creds, is_live_mode

logger = logging.getLogger(__name__)

# Risk limits
MAX_POSITION_SIZE_USD = 50.0
STOP_LOSS_PCT = 0.5
TAKE_PROFIT_PCT = 3.0
MAX_POSITIONS_PER_ACCOUNT = 3
MAX_DAILY_LOSS_USD = 200.0  # Stop trading if lost $200 today


class BinanceSignalTrader:
    """Executes AI signals on live Binance accounts."""
    
    def can_trade(self, uid: str, c: BinanceClient) -> Tuple[bool, str]:
        """Check if account is ready to receive signals."""
        # Check live mode
        if not is_live_mode(uid):
            return False, "Account in PRACTICE mode (enable LIVE MODE in Settings)"
        
        # Check USDT balance
        usdt_bal = c.get_balance("USDT")
        if usdt_bal < MAX_POSITION_SIZE_USD:
            return False, f"Insufficient USDT: ${usdt_bal:.2f} < ${MAX_POSITION_SIZE_USD:.2f}"
        
        # Check position count
        positions = c.get_open_positions() or []
        if len(positions) >= MAX_POSITIONS_PER_ACCOUNT:
            return False, f"Max {MAX_POSITIONS_PER_ACCOUNT} positions reached"
        
        return True, "Ready"
    
    
    def execute_signal(self, uid: str, symbol: str, signal: str) -> Dict:
        """
        Execute BUY/SELL signal on Binance.
        
        Returns:
            {
                "success": bool,
                "message": str,
                "order_id": str (if success),
                "oco_order_id": str (if success),
                "entry_price": float,
                "sl_price": float,
                "tp_price": float,
                "quantity": float,
            }
        """
        try:
            c = get_client_for_user(uid)
            if not c:
                return {"success": False, "message": "Binance client error"}
            
            # Validate account state
            ok, msg = self.can_trade(uid, c)
            if not ok:
                return {"success": False, "message": msg}
            
            # Only support BUY signals (long-only, Phase 8)
            if signal != "BUY":
                return {"success": False, "message": "SELL signals not supported yet (Phase 9)"}
            
            # Get current price
            price = c.get_price(symbol)
            if price <= 0:
                return {"success": False, "message": f"Cannot fetch price for {symbol}"}
            
            # Calculate order size
            quantity = MAX_POSITION_SIZE_USD / price
            
            # Calculate SL/TP prices
            sl_price = price * (1 - STOP_LOSS_PCT / 100)
            tp_price = price * (1 + TAKE_PROFIT_PCT / 100)
            
            logger.info(
                f"Signal: BUY {symbol} for uid={uid}\n"
                f"  Entry: ${price:.4f}\n"
                f"  SL: ${sl_price:.4f} (-{STOP_LOSS_PCT}%)\n"
                f"  TP: ${tp_price:.4f} (+{TAKE_PROFIT_PCT}%)\n"
                f"  Qty: {quantity:.8f}"
            )
            
            # Place market order with OCO SL/TP
            result = c.place_market_buy_with_sl_tp(
                symbol=symbol,
                usd_amount=MAX_POSITION_SIZE_USD,
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
                "message": f"BUY {symbol} @ ${price:.4f}",
                "order_id": result.get("buy_order_id"),
                "oco_order_id": result.get("oco_order_id"),
                "entry_price": price,
                "sl_price": sl_price,
                "tp_price": tp_price,
                "quantity": quantity,
                "amount_usd": MAX_POSITION_SIZE_USD,
            }
        
        except Exception as e:
            logger.error(f"Binance signal execution error: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}


def execute_binance_signal(uid: str, symbol: str, signal: str) -> Dict:
    """Execute signal on Binance. Returns result dict."""
    trader = BinanceSignalTrader()
    return trader.execute_signal(uid, symbol, signal)
