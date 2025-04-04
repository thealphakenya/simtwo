import sys
import os

# Add the 'backend' directory to the Python path to enable imports from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask, request, jsonify
from trading_logic.order_execution import OrderExecution  # Now import correctly after adjusting PYTHONPATH
from binance.enums import SIDE_BUY, SIDE_SELL  # Import both buy and sell options

app = Flask(__name__)

# Initialize API keys (replace with your actual keys)
api_key = "your_api_key"
api_secret = "your_api_secret"

# Instantiate the OrderExecution class with the API keys
order_executor = OrderExecution(api_key, api_secret)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    # Get the data from the POST request
    order_data = request.json
    symbol = order_data['symbol']
    side = order_data['side']
    quantity = order_data['quantity']
    
    # Validate 'side' to ensure it's either 'BUY' or 'SELL'
    if side not in [SIDE_BUY, SIDE_SELL]:
        return jsonify({"status": "error", "message": "Invalid side. Use 'BUY' or 'SELL'."}), 400
    
    # Place the order using the OrderExecution class
    order_response = order_executor.place_market_order(symbol=symbol, side=side, quantity=quantity)
    
    # If the order was successfully placed, return the order details
    if order_response:
        return jsonify({"status": "success", "order": order_response})
    else:
        # If the order couldn't be placed, return an error
        return jsonify({"status": "error", "message": "Failed to place order"}), 400

if __name__ == '__main__':
    # Run the Flask app with debugging enabled
    app.run(debug=True)
