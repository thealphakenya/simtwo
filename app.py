import sys
import os
import logging
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL
from ai_models.model import ReinforcementLearning, NeuralNetwork
from trading_logic.order_execution import OrderExecution, execute_order
from data.data_fetcher import get_market_data

# ===========================
# 📌 Logging Setup
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Log initial sys.path
logging.info("Debug: Initial sys.path in app.py: %s", sys.path)

# Add /app/backend to sys.path if not present
backend_path = "/app/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)
    logging.info("Debug: Added /app/backend to sys.path")

# Confirm updated sys.path
logging.info("Debug: Updated sys.path in app.py: %s", sys.path)

# ===========================
# Binance Client Initialization
# ===========================
binance_api_key = "your_api_key"
binance_api_secret = "your_api_secret"
client = Client(binance_api_key, binance_api_secret)

# AI Models - Store AI strategy state
ai_managed_preferences = True
auto_trade_enabled = False

# ===========================
# 🚀 Flask App Setup
# ===========================
app = Flask(__name__)

# ===========================
# Trading Logic and Routes
# ===========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Flask app!"}), 200

@app.route('/api/market_data', methods=['GET'])
def get_market_data_api():
    # Get real-time market data (e.g., price, volume)
    data = get_market_data('BTCUSDT')  # Example for BTC/USD pair
    return jsonify(data)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    symbol = order_data['symbol']
    quantity = order_data['quantity']
    order_type = order_data['order_type']
    
    # Execute order via Binance API
    result = execute_order(symbol, quantity, order_type)
    return jsonify(result)

@app.route('/api/ai_predict', methods=['POST'])
def ai_predict():
    market_data = request.json
    # Use the AI model to make predictions based on the market data
    if ai_managed_preferences:
        prediction = ReinforcementLearning().predict(market_data)
    else:
        prediction = NeuralNetwork().predict(market_data)
    return jsonify(prediction)

@app.route('/api/set_preferences', methods=['POST'])
def set_preferences():
    global ai_managed_preferences, auto_trade_enabled
    preferences = request.json
    ai_managed_preferences = preferences.get('ai_managed_preferences', ai_managed_preferences)
    auto_trade_enabled = preferences.get('auto_trade_enabled', auto_trade_enabled)
    return jsonify({"status": "Preferences updated", "ai_managed_preferences": ai_managed_preferences, "auto_trade_enabled": auto_trade_enabled})

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    # Run simulation with the current AI strategy
    results = simulate_trading_strategy()
    return jsonify(results)

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    # Stop all trading actions
    stop_trading()
    return jsonify({"status": "Emergency stop activated"})

# ===========================
# Trading Simulation and Stopping Logic
# ===========================

def simulate_trading_strategy():
    # Simulate AI strategy
    return {
        "P&L": 1500,
        "Sharpe Ratio": 1.75,
        "Win Rate": 65,
        "Max Drawdown": -10
    }

def stop_trading():
    # Logic to stop all active trades (e.g., cancel orders, stop AI trading)
    pass

# ===========================
# ⏰ Scheduled Trading Logic
# ===========================

# Initialize OrderExecution for real trading logic
order_executor = OrderExecution(binance_api_key, binance_api_secret)

def run_trading_job():
    try:
        logging.info("Running scheduled trading logic...")

        data = order_executor.fetch_data()  # Use order_executor to fetch market data
        short_sma, long_sma = order_executor.calculate_indicators(data)

        if short_sma and long_sma:
            signal = order_executor.check_trade_signal(short_sma, long_sma)
            if signal:
                order_executor.execute_order(signal)

    except Exception as e:
        logging.error("Trading logic error: %s", str(e))

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()

# Graceful shutdown
import atexit
atexit.register(lambda: scheduler.shutdown())

# ===========================
# ✅ Health Check
# ===========================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ===========================
# 🏃 Run App Locally
# ===========================
if __name__ == "__main__":
    app.run(debug=True)
