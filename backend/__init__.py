import sys
import os

# Add the parent directory to the Python path so that 'backend' can be imported from other scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Core Imports for Convenience
from backend.trading_logic.order_execution import OrderExecution
from backend.config.config import config

# You can also expose frequently used modules or classes here if needed
__all__ = ["OrderExecution", "config"]
