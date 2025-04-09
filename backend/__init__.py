# backend/__init__.py

# Import necessary components for data, trading logic, and AI models
from .data import DataFetcher, get_market_data
from .trading_logic.order_execution import OrderExecution
from .ai_models import TradingAI, ReinforcementLearning

# Optionally, you can define a list of all public-facing modules in the backend
__all__ = [
    "DataFetcher",         # Include DataFetcher for quick access
    "get_market_data",     # Add the convenience function for market data fetching
    "OrderExecution",      # Include OrderExecution to handle orders
    "TradingAI",           # Include TradingAI model
    "ReinforcementLearning",  # Include ReinforcementLearning model
    # Add other modules here if needed, e.g.:
    # "SomeOtherModule",
]
