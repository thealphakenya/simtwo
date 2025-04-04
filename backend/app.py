from flask import Flask, request, jsonify
from backend.trading_logic.order_execution import OrderExecution
from binance.enums import SIDE_BUY, SIDE_SELL  # Import both buy and sell options

app = Flask(__name__)

# Initialize API keys
api_key = "your_api_key"
api_secret = "your_api_secret"

# Instantiate the OrderExecution class
order_executor = OrderExecution(api_key, api_secret)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    symbol = order_data['symbol']
    side = order_data['side']
    quantity = order_data['quantity']
    
    # Validate side value
    if side not in [SIDE_BUY, SIDE_SELL]:
        return jsonify({"status": "error", "message": "Invalid side. Use 'BUY' or 'SELL'."}), 400
    
    # Place the order using OrderExecution
    order_response = order_executor.place_market_order(symbol=symbol, side=side, quantity=quantity)
    
    if order_response:
        return jsonify({"status": "success", "order": order_response})
    else:
        return jsonify({"status": "error", "message": "Failed to place order"}), 400

if __name__ == '__main__':
    app.run(debug=True)
