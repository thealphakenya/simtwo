import os
import sys

# Ensure the current directory (backend) is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import trading logic properly
sys.path.append("/app")

from backend.trading_logic.order_execution import OrderExecution
