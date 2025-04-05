import sys
import os

# Add the parent directory to the Python path so that 'backend' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the OrderExecution class from the trading_logic module
from backend.trading_logic.order_execution import OrderExecution

# Import the config object from the backend/config/config.py file
from backend.config.config import config
