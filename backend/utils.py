import os
import logging

# Accessing environment variables directly using os.getenv
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')
TRADE_SYMBOL = os.getenv('TRADE_SYMBOL', 'BTCUSDT')  # Default to BTCUSDT if not set
TRADE_QUANTITY = float(os.getenv('TRADE_QUANTITY', 0.01))  # Default to 0.01 if not set

# Logging to confirm if the values are fetched correctly
if not API_KEY or not API_SECRET:
    logging.error("Binance API keys not found in environment variables!")

def setup_logger():
    # Example function to demonstrate logger setup
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

def format_response(status: str, data: dict = None):
    return {
        "status": status,
        "data": data or {}
    }

class Timer:
    import time

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = self.time.time()

    def stop(self):
        if self.start_time is None:
            raise RuntimeError("Timer not started.")
        return self.time.time() - self.start_time

# Example helper function that uses the environment variables
def get_safe_position_size(balance):
    """Simple function to calculate safe position size based on balance"""
    if balance <= 0:
        raise ValueError("Invalid balance amount.")
    # Example logic for position sizing
    return balance * 0.01  # Example: trade 1% of the balance