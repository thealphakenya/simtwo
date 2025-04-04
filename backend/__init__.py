import os
import sys

# Ensure the current directory (app) is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Debugging: print the Python path to verify
print("Current sys.path:", sys.path)

# Import from trading_logic
from backend.trading_logic import order_execution
