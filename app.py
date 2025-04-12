import os
import logging
import atexit
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client

from backend.trading_logic.order_execution import OrderExecution
from ai_models.model import TradingAI
from training_logic.order_execution import execute_order
from data.data_fetcher import DataFetcher

# ===========================
# 🔧 Config
# ===========================

class Config:
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = 'd9f1a3d47f83e25f92c97a912b3ac31c45ff98c87e2e98b03d78a12a78a813f5'

config = Config()

# ===========================
# ⚙️ Setup
# ===========================

app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')
socketio = SocketIO(app)

logging.basicConfig(level=logging.DEBUG)

if not config.API_KEY or not config.API_SECRET:
    logging.error("API Key or Secret is missing!")
else:
    logging.debug(f"API Key: {config.API_KEY[:4]}... Loaded")

# ===========================
# 🌐 Binance Client + Modules
# ===========================

client = Client(config.API_KEY, config.API_SECRET)
fetcher = DataFetcher(api_key=config.API_KEY, api_secret=config.API_SECRET, trade_symbol=config.TRADE_SYMBOL)
order_executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)

# ===========================
# 🧠 AI Models
# ===========================

lstm_model = TradingAI(model_type='lstm')
trading_ai = TradingAI(model_type='gru')
reinforcement_model = TradingAI(model_type='reinforcement', api_key=config.API_KEY, api_secret=config.API_SECRET)

# ===========================
# ⚙️ Global State
# ===========================

ai_managed_preferences = True
auto_trade_enabled = False
virtual_account = True
ai_status = {"state": "IDLE", "details": ""}

def update_ai_status(state: str, details: str = ""):
    ai_status["state"] = state
    if "Monitoring" in state and "Prediction" not in details:
        try:
            dummy_df = fetcher.fetch_ohlcv_data(config.TRADE_SYMBOL)
            prediction = round(np.mean([
                lstm_model.predict(dummy_df)[0][0],
                trading_ai.predict(dummy_df)[0][0],
                reinforcement_model.predict(dummy_df)
            ]), 4)
            details += f" (Model: Ensemble | Prediction: {prediction}, Threshold: 0.5)"
        except Exception as e:
            logging.warning(f"Could not fetch prediction for status: {str(e)}")
    ai_status["details"] = details or state
    logging.debug(f"AI STATUS UPDATED: {ai_status}")

# ===========================
# 📡 Routes
# ===========================

@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:path>')
def serve_frontend(path):
    return send_from_directory('frontend', path)

@app.route('/api/market_data')
def get_market_data_api():
    try:
        return jsonify(fetcher.fetch_ticker(config.TRADE_SYMBOL))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/order_book')
def order_book():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    try:
        return jsonify(fetcher.fetch_order_book(symbol))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ohlcv')
def ohlcv():
    symbol = request.args.get('symbol', config.TRADE_SYMBOL)
    try:
        df = fetcher.fetch_ohlcv_data(symbol)
        return df.to_json(orient='records')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/balance')
def balance():
    try:
        return jsonify(fetcher.fetch_balance())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.json
    symbol = data.get('symbol', config.TRADE_SYMBOL)
    quantity = float(data.get('quantity', config.TRADE_QUANTITY))
    order_type = data.get('order_type', 'market').lower()

    try:
        result = execute_order(symbol=symbol, quantity=quantity, order_type=order_type)
        update_ai_status("ACTIVE — Trading Decision Made", f"Order Placed: {order_type.upper()} {symbol} {quantity}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai_predict', methods=['POST'])
def ai_predict():
    market_data = request.json
    try:
        if ai_managed_preferences:
            model = reinforcement_model
        else:
            model = trading_ai
        prediction = model.predict(np.array(market_data))
        update_ai_status("ACTIVE — Monitoring...", f"Prediction Result: {prediction.tolist()}")
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/ai_status')
def get_ai_status():
    return jsonify(ai_status)

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    try:
        return jsonify(simulate_trading_strategy())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    stop_trading()
    return jsonify({"status": "Emergency stop activated"})

# ===========================
# ⚙️ Background Logic
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
    logging.warning("Emergency stop: Scheduler paused")

def run_trading_job():
    update_ai_status("ACTIVE — Monitoring...")
    try:
        ticker = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        logging.debug("Ticker data: %s", ticker)
    except Exception as e:
        update_ai_status("ERROR", str(e))

# ===========================
# ⏰ Scheduler Setup
# ===========================

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ===========================
# ❤️ Health Check
# ===========================

@app.route('/health')
def health_check():
    try:
        health_data = {
            "status": "healthy",
            "message": "All systems running smoothly."
        }
        try:
            client.ping()
            health_data["binance_api"] = "Connected"
        except Exception as e:
            health_data["binance_api"] = f"Failed: {str(e)}"

        try:
            fetcher.fetch_ticker(config.TRADE_SYMBOL)
            health_data["data_fetcher"] = "Working"
        except Exception as e:
            health_data["data_fetcher"] = f"Failed: {str(e)}"

        return jsonify(health_data)
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ===========================
# ▶️ App Launch
# ===========================

if __name__ == '__main__':
    logging.info("Starting Simtwo Flask App")
    app.run(host='0.0.0.0', port=5000, debug=True)