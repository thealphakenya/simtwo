import sys
import os

# Add the parent directory to the path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.trading_logic.order_execution import OrderExecution
from backend.config import config  # ✅ this works because of __init__.py in config

__all__ = ["OrderExecution", "config"]
