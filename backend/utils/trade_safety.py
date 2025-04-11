import logging
import os
from backend.victorq.neutralizer import TradingHelper

# Constants for position safety
MAX_POSITION_RATIO = 0.5
MIN_POSITION_SIZE = 0.001

# Set logging level from environment variable, default to DEBUG
LOGGING_LEVEL = os.getenv("TRADE_HELPER_LOGGING", "DEBUG").upper()
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL, logging.DEBUG))

def get_safe_position_size(balance: float, verbose: bool = True) -> float:
    """
    Calculate a safe trading position size based on account balance.
    Caps size to avoid overexposure, logs calculations for transparency.
    """
    try:
        raw_size = TradingHelper.calculate_position_size(balance)

        if verbose:
            logging.debug(f"[TradeHelper] Raw position size from balance {balance:.4f}: {raw_size:.6f}")

        if raw_size <= 0:
            logging.warning(f"[TradeHelper] Invalid size {raw_size}, using minimum {MIN_POSITION_SIZE}")
            return MIN_POSITION_SIZE

        capped_size = min(raw_size, balance * MAX_POSITION_RATIO)

        if capped_size < raw_size:
            logging.info(f"[TradeHelper] Position size capped from {raw_size:.6f} to {capped_size:.6f}.")

        return round(max(capped_size, MIN_POSITION_SIZE), 6)

    except Exception as e:
        logging.error(f"[TradeHelper] Error calculating position size: {e}")
        return MIN_POSITION_SIZE