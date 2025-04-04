import os
import sys

# Ensure the parent directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.trading_logic import order_execution  # Explicit absolute import
