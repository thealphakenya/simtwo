# backend/__init__.py

# Import necessary components for trading logic and other backend operations
from backend.trading_logic.order_execution import OrderExecution

# You can add any other necessary imports from the backend here

# Optionally, you can define a list of all public-facing modules in the backend
__all__ = [
    "OrderExecution",
    # Add other modules here if needed, for example:
    # "SomeOtherModule",
]
