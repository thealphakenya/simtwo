from flask import Flask, request, jsonify
from binance.enums import SIDE_BUY, SIDE_SELL  # Import both buy and sell options
from backend.trading_logic.order_execution import OrderExecution  # Correct import path

app = Flask(__name__)

# Initialize API keys (replace with actual credentials)
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Instantiate the OrderExecution class with the API keys
order_executor = OrderExecution(API_KEY, API_SECRET)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    """
    Handles market order placement via API.
    Expects JSON input: {"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.01}
    """
    try:
        order_data = request.get_json()
        symbol = order_data.get("symbol")
        side = order_data.get("side")
        quantity = order_data.get("quantity")

        # Validate required parameters
        if not symbol or not side or not quantity:
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        if side not in [SIDE_BUY, SIDE_SELL]:
            return jsonify({"status": "error", "message": "Invalid side. Use 'BUY' or 'SELL'."}), 400

        # Execute the order
        order_response = order_executor.place_market_order(symbol, side, quantity)

        if order_response:
            return jsonify({"status": "success", "order": order_response}), 200
        else:
            return jsonify({"status": "error", "message": "Order execution failed."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
