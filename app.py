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
from ai_models.model import ReinforcementLearning, NeuralNetwork
from trading_logic.order_execution import OrderExecution, execute_order
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
    return jsonify({"message": "Welcome to Simtwo Trading API"}), 200

@app.route('/api/market_data', methods=['GET'])
def get_market_data_api():
    data = fetcher.fetch_ticker(config.TRADE_SYMBOL)
    return jsonify(data)

@app.route('/api/order_book', methods=['GET'])
def order_book():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    return jsonify(fetcher.fetch_order_book(symbol))

@app.route('/api/ohlcv', methods=['GET'])
def ohlcv():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    df = fetcher.fetch_ohlcv_data(symbol)
    return df.to_json(orient='records')

@app.route('/api/balance', methods=['GET'])
def balance():
    return jsonify(fetcher.fetch_balance())

@app.route('/api/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    symbol = order_data.get('symbol', config.TRADE_SYMBOL)
    quantity = float(order_data.get('quantity', config.TRADE_QUANTITY))
    order_type = order_data.get('order_type', 'market').lower()

    result = execute_order(symbol=symbol, quantity=quantity, order_type=order_type)
    return jsonify(result)

@app.route('/api/ai_predict', methods=['POST'])
def ai_predict():
    market_data = request.json
    if ai_managed_preferences:
        prediction = ReinforcementLearning().predict(market_data)
    else:
        prediction = NeuralNetwork().predict(market_data)
    return jsonify({"prediction": prediction})

@app.route('/api/set_preferences', methods=['POST'])
def set_preferences():
    global ai_managed_preferences, auto_trade_enabled
    prefs = request.json
    ai_managed_preferences = prefs.get('ai_managed_preferences', ai_managed_preferences)
    auto_trade_enabled = prefs.get('auto_trade_enabled', auto_trade_enabled)
    return jsonify({
        "status": "Preferences updated",
        "ai_managed_preferences": ai_managed_preferences,
        "auto_trade_enabled": auto_trade_enabled
    })

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    results = simulate_trading_strategy()
    return jsonify(results)

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    stop_trading()
    return jsonify({"status": "Emergency stop activated"})

# ===========================
# 📡 Webhook Listener
# ===========================
def verify_webhook_signature(request):
    received_sig = request.headers.get('X-Signature')
    if not received_sig:
        return False

    computed_sig = hmac.new(
        key=config.WEBHOOK_SECRET.encode(),
        msg=request.get_data(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(received_sig, computed_sig)

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    if not verify_webhook_signature(request):
        logging.warning("🚫 Webhook signature verification failed!")
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
    # Optional: Slack, Discord, email integration

# ===========================
# 📊 Simulated Trading Logic
# ===========================
def simulate_trading_strategy():
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
    try:
        logging.info("⏰ Running scheduled trading job...")
        ticker = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        # Add AI logic if needed
    except Exception as e:
        logging.error(f"Error in scheduled job: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

# ===========================
# 💓 Health Check Endpoint
# ===========================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ===========================
# 🏁 Start App
# ===========================
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Starting Simtwo Flask App")
    app.run(debug=True)
