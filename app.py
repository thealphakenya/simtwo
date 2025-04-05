import sys
import os
import logging
import atexit
import hmac
import hashlib
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from binance.enums import SIDE_BUY, SIDE_SELL
from binance.client import Client

# ===========================
# 🔧 Add /backend to sys.path
# ===========================
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# ===========================
# 📦 Backend Module Imports
# ===========================
from ai_models.model import ReinforcementLearning, NeuralNetwork  # Import the ReinforcementLearning class
from training_logic.order_execution import OrderExecution, execute_order  # Updated import
from data.data_fetcher import DataFetcher
from config import config

# ===========================
# 🔐 API Setup
# ===========================
client = Client(config.API_KEY, config.API_SECRET)
fetcher = DataFetcher(config.API_KEY, config.API_SECRET)
order_executor = OrderExecution(config.API_KEY, config.API_SECRET)

# ===========================
# 🚀 Flask App Setup
# ===========================
app = Flask(__name__)

# ===========================
# ⚙️ Global State
# ===========================
ai_managed_preferences = True
auto_trade_enabled = False

# ===========================
# 🔁 API Routes
# ===========================

@app.route('/')
def home():
    logging.debug("Handling home route request")
    return jsonify({"message": "Welcome to Simtwo Trading API"}), 200

@app.route('/api/market_data', methods=['GET'])
def get_market_data_api():
    logging.debug("Fetching market data for %s", config.TRADE_SYMBOL)
    try:
        data = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        return jsonify(data)
    except Exception as e:
        logging.error("Error fetching market data: %s", str(e))
        return jsonify({"error": "Error fetching market data", "details": str(e)}), 500

@app.route('/api/order_book', methods=['GET'])
def order_book():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    logging.debug("Fetching order book for symbol: %s", symbol)
    try:
        order_data = fetcher.fetch_order_book(symbol)
        return jsonify(order_data)
    except Exception as e:
        logging.error("Error fetching order book: %s", str(e))
        return jsonify({"error": "Error fetching order book", "details": str(e)}), 500

@app.route('/api/ohlcv', methods=['GET'])
def ohlcv():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    logging.debug("Fetching OHLCV data for symbol: %s", symbol)
    try:
        df = fetcher.fetch_ohlcv_data(symbol)
        return df.to_json(orient='records')
    except Exception as e:
        logging.error("Error fetching OHLCV data: %s", str(e))
        return jsonify({"error": "Error fetching OHLCV data", "details": str(e)}), 500

@app.route('/api/balance', methods=['GET'])
def balance():
    logging.debug("Fetching account balance")
    try:
        balance_data = fetcher.fetch_balance()
        return jsonify(balance_data)
    except Exception as e:
        logging.error("Error fetching balance: %s", str(e))
        return jsonify({"error": "Error fetching balance", "details": str(e)}), 500

@app.route('/api/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    symbol = order_data.get('symbol', config.TRADE_SYMBOL)
    quantity = float(order_data.get('quantity', config.TRADE_QUANTITY))
    order_type = order_data.get('order_type', 'market').lower()

    logging.debug("Placing order: symbol=%s, quantity=%f, order_type=%s", symbol, quantity, order_type)
    try:
        result = execute_order(symbol=symbol, quantity=quantity, order_type=order_type)
        return jsonify(result)
    except Exception as e:
        logging.error("Error placing order: %s", str(e))
        return jsonify({"error": "Error placing order", "details": str(e)}), 500

@app.route('/api/ai_predict', methods=['POST'])
def ai_predict():
    market_data = request.json
    logging.debug("Predicting AI model based on market data")
    try:
        if ai_managed_preferences:
            prediction = ReinforcementLearning().predict(market_data)  # Using ReinforcementLearning class
        else:
            prediction = NeuralNetwork().predict(market_data)  # Fallback to NeuralNetwork class
        return jsonify({"prediction": prediction})
    except Exception as e:
        logging.error("Error during AI prediction: %s", str(e))
        return jsonify({"error": "Error during AI prediction", "details": str(e)}), 500

@app.route('/api/set_preferences', methods=['POST'])
def set_preferences():
    global ai_managed_preferences, auto_trade_enabled
    prefs = request.json
    ai_managed_preferences = prefs.get('ai_managed_preferences', ai_managed_preferences)
    auto_trade_enabled = prefs.get('auto_trade_enabled', auto_trade_enabled)
    logging.debug("Updated preferences: ai_managed_preferences=%s, auto_trade_enabled=%s", ai_managed_preferences, auto_trade_enabled)
    return jsonify({
        "status": "Preferences updated",
        "ai_managed_preferences": ai_managed_preferences,
        "auto_trade_enabled": auto_trade_enabled
    })

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    logging.debug("Running simulation")
    try:
        results = simulate_trading_strategy()
        return jsonify(results)
    except Exception as e:
        logging.error("Error running simulation: %s", str(e))
        return jsonify({"error": "Error running simulation", "details": str(e)}), 500

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    logging.warning("Emergency stop activated")
    stop_trading()
    return jsonify({"status": "Emergency stop activated"})

# ===========================
# 📡 Webhook Listener
# ===========================
def verify_webhook_signature(request):
    received_sig = request.headers.get('X-Signature')
    if not received_sig:
        logging.warning("🚫 Webhook signature missing!")
        return False

    computed_sig = hmac.new(
        key=config.WEBHOOK_SECRET.encode(),
        msg=request.get_data(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(received_sig, computed_sig):
        logging.warning("🚫 Webhook signature mismatch!")
        return False
    return True

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    if not verify_webhook_signature(request):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.json
    event_type = event.get('event', '')
    status = event.get('status', '')

    logging.info(f"📬 Webhook received: {event_type}, status: {status}")

    if 'build' in event_type:
        if status == 'success':
            logging.info("✅ Build succeeded.")
            notify_team("✅ Build succeeded on Railway.")
        elif status == 'failed':
            logging.error("❌ Build failed.")
            notify_team("❌ Build failed. Check the logs.")
    elif 'deploy' in event_type:
        if status == 'success':
            logging.info("🚀 Deployment succeeded.")
            notify_team("🚀 Deployment completed successfully.")
        elif status == 'failed':
            logging.error("🔥 Deployment failed.")
            notify_team("🔥 Deployment failed. Manual intervention may be needed.")

    return jsonify({"status": "Webhook received"}), 200

def notify_team(message):
    logging.info(f"📣 Team Notification: {message}")

# ===========================
# 📊 Simulated Trading Logic
# ===========================
def simulate_trading_strategy():
    logging.debug("Simulating trading strategy")
    return {
        "P&L": 1500,
        "Sharpe Ratio": 1.75,
        "Win Rate": 65,
        "Max Drawdown": -10
    }

def stop_trading():
    scheduler.pause()
    logging.warning("🚨 Emergency stop: Scheduler paused")

# ===========================
# ⏰ Background Trading Job
# ===========================
def run_trading_job():
    logging.info("⏰ Running scheduled trading job...")
    try:
        ticker = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        logging.debug("Ticker data: %s", ticker)
    except Exception as e:
        logging.error("Error in scheduled trading job: %s", str(e))

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

# ===========================
# 💓 Health Check Endpoint
# ===========================
@app.route('/health', methods=['GET'])
def health_check():
    logging.debug("Health check initiated.")
    try:
        health_data = {
            "status": "healthy",
            "message": "All systems are running smoothly."
        }

        try:
            client.ping()
            health_data["binance_api"] = "Connected"
        except Exception as e:
            health_data["binance_api"] = f"Failed: {str(e)}"
            logging.error("Error with Binance API: %s", str(e))

        try:
            fetcher.fetch_ticker(config.TRADE_SYMBOL)
            health_data["data_fetcher"] = "Working"
        except Exception as e:
            health_data["data_fetcher"] = f"Failed: {str(e)}"
            logging.error("Error with DataFetcher: %s", str(e))

        return jsonify(health_data), 200
    except Exception as e:
        logging.error("Health check failed: %s", str(e))
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ===========================
# 🏁 Start App
# ===========================
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("🚀 Starting Simtwo Flask App")
    app.run(host='0.0.0.0', port=5000, debug=True)
