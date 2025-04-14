import os
import logging
import hmac
import hashlib
import threading
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_socketio import SocketIO
from binance.client import Client

from backend.trading_logic.order_execution import OrderExecution, TradingLogic
from backend.ai_models.reinforcement_learning import ReinforcementLearning
from backend.ai_models.neural_network import NeuralNetwork
from backend.ai_models.lstm_model import LSTMTradingModel
from backend.data.data_fetcher import DataFetcher
from backend.tasks import run_trading_job_task  # Import the Celery task

# ===========================
# ⚙️ Configuration
# ===========================
class Config:
    ENV = os.getenv("ENV", "dev")  # 'prod' or 'dev'
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET') or 'demo_secret'
    USE_EXTERNAL_DATA = ENV == 'prod'

config = Config()

# ===========================
# 🚀 Flask Setup
# ===========================
app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')
socketio = SocketIO(app)

# ===========================
# 🔐 Binance Client Setup
# ===========================
client = None
if config.USE_EXTERNAL_DATA:
    try:
        client = Client(config.API_KEY, config.API_SECRET)
    except Exception as e:
        logging.error(f"Error initializing Binance Client: {str(e)}")
        raise
else:
    logging.info("Running in DEV mode - using simulated data")

# ===========================
# 🧠 AI + Trading Components
# ===========================
fetcher = DataFetcher(
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
    trade_symbol=config.TRADE_SYMBOL,
    use_external=config.USE_EXTERNAL_DATA
)
order_executor = OrderExecution(config.API_KEY, config.API_SECRET)

# ===========================
# ⚙️ Global State
# ===========================
ai_managed_preferences = True
auto_trade_enabled = False
bot_running = False
bot_thread = None

# ===========================
# 🔁 API Routes
# ===========================
@app.route('/')
def home():
    return render_template('index.html', bot_running=bot_running)

@app.route('/frontend/<path:path>')
def serve_frontend(path):
    return send_from_directory('frontend', path)

@app.route('/api/status', methods=['GET'])
def bot_status():
    return jsonify({"bot_running": bot_running})

@app.route('/api/start_stop_bot', methods=['POST'])
def start_stop_bot():
    global bot_running, bot_thread
    if bot_running:
        stop_bot()
        return jsonify({"status": "Bot stopped"})
    else:
        start_bot()
        return jsonify({"status": "Bot started"})

# ===========================
# 🤖 Bot Logic
# ===========================
def start_bot():
    global bot_running
    if not bot_running:
        bot_running = True
        # Use Celery to run the trading job in the background
        run_trading_job_task.delay()  # Trigger the Celery task
        logging.info("Trading bot started")

def stop_bot():
    global bot_running
    bot_running = False
    logging.info("Trading bot stopped")

# ===========================
# 📡 Webhook Verification
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
    logging.info(f"📬 Webhook received: {event.get('event')} | status: {event.get('status')}")
    return jsonify({"status": "Webhook received"}), 200

# ===========================
# 🏁 Launch App
# ===========================
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("🚀 Starting Flask Trading Bot App")
    app.run(host='0.0.0.0', port=5000, debug=config.ENV != 'prod')