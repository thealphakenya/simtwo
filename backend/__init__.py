# Import necessary components for trading logic and other backend operations
from backend.trading_logic.order_execution import OrderExecution
from backend.ai_models import TradingAI, ReinforcementLearning  # Add the AI models

# You can add any other necessary imports from the backend here

# Optionally, you can define a list of all public-facing modules in the backend
__all__ = [
    "OrderExecution",
    "TradingAI",  # Add TradingAI to the list
    "ReinforcementLearning",  # Add ReinforcementLearning to the list
    # Add other modules here if needed, for example:
    # "SomeOtherModule",
]
