#!/usr/bin/env python3
"""
OpenAsset AI Signal Engine — Technical Analysis & Auto-Trading
===============================================================

Generates buy/sell signals using:
  • RSI (Relative Strength Index) — momentum
  • MACD (Moving Average Convergence Divergence) — trend
  • Bollinger Bands — volatility
  • EMA (Exponential Moving Average) — trend direction

Signals are generated on 1h/4h/daily candles and can auto-execute
in Strategy Lab or live platforms (Binance/Alpaca/OANDA).

Risk management:
  • Max position size: $50 USD (configurable)
  • Stop loss: 0.5% (configurable)
  • Take profit: 3.0% (configurable)
  • Max concurrent signals: 3 per account
"""

import json
import logging
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone, timedelta
from collections import deque

logger = logging.getLogger(__name__)

# ─── Configuration ──────────────────────────────────────────────────────────────
DB_PATH = "/root/openasset_club/telegram_bot/database"

# RSI thresholds
RSI_OVERSOLD = 30        # Buy signal
RSI_OVERBOUGHT = 70      # Sell signal
RSI_PERIOD = 14

# MACD periods
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2.0

# Trading config
MAX_SIGNALS_PER_ACCOUNT = 3
SIGNAL_COOLDOWN = 300    # seconds (prevent spamming)
CANDLE_PERIOD = 3600     # 1 hour


# ─── Technical Indicators ────────────────────────────────────────────────────────
def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Simple Moving Average."""
    if len(prices) < period:
        return [None] * len(prices)
    sma = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        sma.append(sum(prices[i-period+1:i+1]) / period)
    return sma


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Exponential Moving Average."""
    if len(prices) < period:
        return [None] * len(prices)
    
    ema = [None] * (period - 1)
    sma = sum(prices[:period]) / period
    ema.append(sma)
    
    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        ema_val = prices[i] * multiplier + ema[-1] * (1 - multiplier)
        ema.append(ema_val)
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Relative Strength Index (0-100)."""
    if len(prices) < period + 1:
        return [None] * len(prices)
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi_list = [None] * period
    
    for i in range(period, len(prices)):
        if i > period:
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs >= 0 else 0
        rsi_list.append(rsi)
    
    return rsi_list


def calculate_macd(prices: List[float], 
                   fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List, List, List]:
    """
    MACD (Moving Average Convergence Divergence).
    Returns: (macd_line, signal_line, histogram)
    """
    if len(prices) < slow:
        return [None]*len(prices), [None]*len(prices), [None]*len(prices)
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = [f - s if f is not None and s is not None else None 
                 for f, s in zip(ema_fast, ema_slow)]
    
    signal_line = calculate_ema(macd_line, signal)
    
    histogram = [m - s if m is not None and s is not None else None 
                 for m, s in zip(macd_line, signal_line)]
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: List[float], 
                              period: int = 20, std_dev: float = 2.0) -> Tuple[List, List, List]:
    """
    Bollinger Bands: (upper_band, middle_band, lower_band).
    """
    if len(prices) < period:
        return [None]*len(prices), [None]*len(prices), [None]*len(prices)
    
    middle = calculate_sma(prices, period)
    
    upper = [None] * (period - 1)
    lower = [None] * (period - 1)
    
    for i in range(period - 1, len(prices)):
        subset = prices[i-period+1:i+1]
        mean = sum(subset) / period
        variance = sum((p - mean)**2 for p in subset) / period
        std = variance ** 0.5
        upper.append(mean + std_dev * std)
        lower.append(mean - std_dev * std)
    
    return upper, middle, lower


# ─── Signal Generation ──────────────────────────────────────────────────────────
class SignalGenerator:
    """Generates buy/sell signals from price data."""
    
    def __init__(self):
        self.last_signal_time: Dict[str, float] = {}  # symbol → timestamp
    
    def can_signal(self, symbol: str) -> bool:
        """Check if enough time has passed since last signal."""
        last = self.last_signal_time.get(symbol, 0)
        return time.time() - last >= SIGNAL_COOLDOWN
    
    def rsi_signal(self, prices: List[float]) -> Optional[str]:
        """
        RSI-based signal.
        Returns: 'BUY', 'SELL', or None.
        """
        if len(prices) < RSI_PERIOD + 1:
            return None
        
        rsi = calculate_rsi(prices, RSI_PERIOD)[-1]
        if rsi is None:
            return None
        
        if rsi < RSI_OVERSOLD:
            return "BUY"
        elif rsi > RSI_OVERBOUGHT:
            return "SELL"
        return None
    
    def macd_signal(self, prices: List[float]) -> Optional[str]:
        """
        MACD-based signal (crossover).
        Returns: 'BUY', 'SELL', or None.
        """
        if len(prices) < 30:
            return None
        
        macd, signal, _ = calculate_macd(prices, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
        
        if len(macd) < 2 or len(signal) < 2:
            return None
        
        m1, m2 = macd[-2], macd[-1]
        s1, s2 = signal[-2], signal[-1]
        
        if m1 is None or m2 is None or s1 is None or s2 is None:
            return None
        
        # Crossover detection
        if m1 <= s1 and m2 > s2:
            return "BUY"
        elif m1 >= s1 and m2 < s2:
            return "SELL"
        return None
    
    def bollinger_signal(self, prices: List[float]) -> Optional[str]:
        """
        Bollinger Bands signal.
        Returns: 'BUY', 'SELL', or None.
        """
        if len(prices) < BB_PERIOD:
            return None
        
        upper, middle, lower = calculate_bollinger_bands(prices, BB_PERIOD, BB_STD_DEV)
        
        u, m, l = upper[-1], middle[-1], lower[-1]
        price = prices[-1]
        
        if l is None or u is None or m is None:
            return None
        
        # Price touches lower band = oversold = BUY
        if price <= l * 1.01:  # Within 1% of lower band
            return "BUY"
        # Price touches upper band = overbought = SELL
        elif price >= u * 0.99:
            return "SELL"
        return None
    
    def generate_signal(self, symbol: str, prices: List[float]) -> Optional[str]:
        """
        Generate consolidated signal from multiple indicators.
        Uses majority vote (2+ of 3 indicators agree).
        """
        if not self.can_signal(symbol):
            return None
        
        signals = []
        
        # RSI signal
        rsi_sig = self.rsi_signal(prices)
        if rsi_sig:
            signals.append(rsi_sig)
        
        # MACD signal
        macd_sig = self.macd_signal(prices)
        if macd_sig:
            signals.append(macd_sig)
        
        # Bollinger Bands signal
        bb_sig = self.bollinger_signal(prices)
        if bb_sig:
            signals.append(bb_sig)
        
        # Majority vote (2+ agreements)
        if len(signals) >= 2:
            if signals.count("BUY") >= 2:
                self.last_signal_time[symbol] = time.time()
                return "BUY"
            elif signals.count("SELL") >= 2:
                self.last_signal_time[symbol] = time.time()
                return "SELL"
        
        return None


# ─── Configuration Management ──────────────────────────────────────────────────
def load_signal_config(uid: str) -> dict:
    """Load signal configuration for user."""
    try:
        with open(f"{DB_PATH}/signal_config.json") as f:
            config = json.load(f)
            return config.get(str(uid), {
                "enabled": False,
                "mode": "stratlab",  # stratlab, binance, alpaca, oanda
                "symbols": ["BTC", "SPY", "EUR"],
                "position_size": 50.0,
                "stop_loss_pct": 0.5,
                "take_profit_pct": 3.0,
            })
    except FileNotFoundError:
        return {}


def save_signal_config(uid: str, config: dict):
    """Save signal configuration for user."""
    try:
        with open(f"{DB_PATH}/signal_config.json") as f:
            all_config = json.load(f)
    except FileNotFoundError:
        all_config = {}
    
    all_config[str(uid)] = config
    
    with open(f"{DB_PATH}/signal_config.json", "w") as f:
        json.dump(all_config, f, indent=2)


def load_signal_stats(uid: str) -> dict:
    """Load signal performance stats."""
    try:
        with open(f"{DB_PATH}/signal_stats.json") as f:
            stats = json.load(f)
            return stats.get(str(uid), {
                "total_signals": 0,
                "winning_signals": 0,
                "losing_signals": 0,
                "last_signal": None,
                "last_signal_symbol": None,
                "win_rate": 0.0,
            })
    except FileNotFoundError:
        return {}


def save_signal_stats(uid: str, stats: dict):
    """Save signal performance stats."""
    try:
        with open(f"{DB_PATH}/signal_stats.json") as f:
            all_stats = json.load(f)
    except FileNotFoundError:
        all_stats = {}
    
    all_stats[str(uid)] = stats
    
    with open(f"{DB_PATH}/signal_stats.json", "w") as f:
        json.dump(all_stats, f, indent=2)


# ─── Utilities ──────────────────────────────────────────────────────────────────
def record_signal(uid: str, symbol: str, signal_type: str, price: float, action: str = "generated"):
    """Record a signal event."""
    signals_log = f"{DB_PATH}/signal_log.json"
    try:
        with open(signals_log) as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []
    
    log.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uid": str(uid),
        "symbol": symbol,
        "signal": signal_type,
        "price": price,
        "action": action,
    })
    
    # Keep last 1000 signals
    log = log[-1000:]
    
    with open(signals_log, "w") as f:
        json.dump(log, f, indent=2)


def get_signal_performance(uid: str) -> dict:
    """Calculate signal win rate and stats."""
    try:
        with open(f"{DB_PATH}/signal_log.json") as f:
            log = json.load(f)
    except FileNotFoundError:
        return {"total": 0, "wins": 0, "losses": 0, "rate": 0}
    
    user_signals = [s for s in log if s.get("uid") == str(uid) and s.get("action") == "closed"]
    
    if not user_signals:
        return {"total": 0, "wins": 0, "losses": 0, "rate": 0}
    
    wins = sum(1 for s in user_signals if s.get("signal") == "WIN")
    losses = sum(1 for s in user_signals if s.get("signal") == "LOSS")
    total = wins + losses
    rate = (wins / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "rate": round(rate, 1),
    }
