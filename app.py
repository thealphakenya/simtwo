import sys
import os
import logging
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from binance.enums import SIDE_BUY, SIDE_SELL

# Set up proper logging configuration for Gunicorn
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Stream logs to standard output (stdout)
    ]
)

# Log sys.path to ensure backend directory is included
logging.info("Debug: Initial sys.path in app.py: %s", sys.path)

# Ensure backend directory is on the path (only necessary if running standalone)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Add the current directory to sys.path

# Log sys.path again to confirm the path update
logging.info("Debug: Updated sys.path in app.py: %s", sys.path)

# Attempt to import OrderExecution and TradingLogic and log any issues
try:
    from backend.trading_logic.order_execution import OrderExecution, TradingLogic
    logging.info("Debug: Successfully imported OrderExecution and TradingLogic")
except ModuleNotFoundError as e:
    logging.error("Debug: ModuleNotFoundError: %s", e)
    raise

# Initialize the Flask app
app = Flask(__name__)

# Replace with your real Binance API keys in production
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

order_executor = OrderExecution(API_KEY, API_SECRET)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    try:
        order_data = request.get_json()
        symbol = order_data.get("symbol")
        side = order_data.get("side")
        quantity = order_data.get("quantity")

        if not symbol or not side or not quantity:
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        if side not in [SIDE_BUY, SIDE_SELL]:
            return jsonify({"status": "error", "message": "Invalid side. Use 'BUY' or 'SELL'."}), 400

        order_response = order_executor.place_market_order(symbol, side, quantity)

        if order_response:
            return jsonify({"status": "success", "order": order_response}), 200
        else:
            return jsonify({"status": "error", "message": "Order execution failed."}), 500

    except Exception as e:
        logging.error("Error in place_order endpoint: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


# ===========================
# ⏰ TradingLogic Scheduler
# ===========================

trading_logic = TradingLogic(API_KEY, API_SECRET)

def run_trading_job():
    try:
        logging.info("Running scheduled trading logic...")

        data = trading_logic.fetch_data()
        short_sma, long_sma = trading_logic.calculate_indicators(data)

        if short_sma and long_sma:
            signal = trading_logic.check_trade_signal(short_sma, long_sma)
            if signal:
                trading_logic.execute_order(signal)

    except Exception as e:
        logging.error("Trading logic error: %s", str(e))

# Set up APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()

# Graceful shutdown
import atexit
atexit.register(lambda: scheduler.shutdown())

# ===========================
# ✅ Health Check Endpoint
# ===========================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ===========================
# 🚀 App Run
# ===========================
if __name__ == "__main__":
    app.run(debug=True)
