import os
from backend.trading_logic.order_execution import OrderExecution
from binance.enums import SIDE_BUY  # Import necessary enums for trade actions

# Ensure API keys are securely stored in environment variables (do not hardcode them)
api_key = os.getenv("BINANCE_API_KEY")  # Get API key from environment variables
api_secret = os.getenv("BINANCE_API_SECRET")  # Get API secret from environment variables

# Check if API keys are available
if not api_key or not api_secret:
    raise ValueError("API key and secret must be set in environment variables.")

# Instantiate the OrderExecution class
order_executor = OrderExecution(api_key, api_secret)

# Example: Place a market buy order for 0.1 BTC
order_response = order_executor.place_market_order(symbol='BTCUSDT', side=SIDE_BUY, quantity=0.1)

# Check if the order was successfully placed
if order_response:
    print("Market order placed successfully:", order_response)
else:
    print("Error placing market order.")
