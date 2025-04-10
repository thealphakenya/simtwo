# trading_logic/__init__.py

# Import order execution logic and the TradingLogic class
from .order_execution import OrderExecution, TradingLogic

# Optionally, you can define a list of all public-facing modules in the trading_logic package
__all__ = [
    "OrderExecution",             # Include OrderExecution to handle orders
    "TradingLogic",               # Include TradingLogic for the strategy and execution
]