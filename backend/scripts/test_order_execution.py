from backend.trading_logic.order_execution import OrderExecution
from binance.enums import SIDE_BUY  # Import necessary enums for trade actions

# Initialize API keys (you should store these securely in environment variables, not hardcode them)
api_key = "your_api_key"
api_secret = "your_api_secret"

# Instantiate the OrderExecution class
order_executor = OrderExecution(api_key, api_secret)

# Example: Place a market buy order for 0.1 BTC
order_response = order_executor.place_market_order(symbol='BTCUSDT', side=SIDE_BUY, quantity=0.1)

# Check if the order was successfully placed
if order_response:
    print("Market order placed successfully:", order_response)
else:
    print("Error placing market order.")
