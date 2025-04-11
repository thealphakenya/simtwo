# Import necessary components for data, trading logic, and AI models
from .data import DataFetcher, get_market_data
from .trading_logic.order_execution import OrderExecution
from .ai_models import LSTMTradingModel, GRUTradingModel, TransformerTradingModel, TradingAI, ReinforcementLearning  # Updated import

# Optionally, you can define a list of all public-facing modules in the backend
__all__ = [
    "DataFetcher",               # Include DataFetcher for quick access
    "get_market_data",           # Add the convenience function for market data fetching
    "OrderExecution",            # Include OrderExecution to handle orders
    "LSTMTradingModel",          # Include LSTM model
    "GRUTradingModel",           # Include GRU model
    "TransformerTradingModel",   # Include Transformer model
    "TradingAI",                 # Include TradingAI for model management and prediction
    "ReinforcementLearning",     # Include ReinforcementLearning for reinforcement learning models
]
