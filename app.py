import os
import logging
import atexit
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client
import numpy as np
from tensorflow.keras.layers import Input  # Import Input layer from Keras

# ===========================
# 📦 AI Trading Integration
# ===========================
from backend.ai_models import TradingAI, ReinforcementLearning

# ===========================
# 📦 Configuration
# ===========================
class Config:
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = 'd9f1a3d47f83e25f92c97a912b3ac31c45ff98c87e2e98b03d78a12a78a813f5'

config = Config()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
API_KEY = config.API_KEY
API_SECRET = config.API_SECRET

if not API_KEY or not API_SECRET:
    logging.error("API Key or Secret is missing!")
else:
    logging.debug(f"API Key: {API_KEY}, API Secret: {API_SECRET}")

# ===========================
# 📦 Backend Module Imports
# ===========================
from backend.trading_logic.order_execution import OrderExecution, TradingLogic
from training_logic.order_execution import execute_order
from data.data_fetcher import DataFetcher

# ===========================
# 🔐 API Setup
# ===========================
try:
    client = Client(config.API_KEY, config.API_SECRET)
except Exception as e:
    logging.error(f"Error initializing Binance Client: {str(e)}")
    raise

fetcher = DataFetcher(api_key=config.API_KEY, api_secret=config.API_SECRET, trade_symbol=config.TRADE_SYMBOL)
order_executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)

# Initialize TradingAI and ReinforcementLearning models
ai_trader = TradingAI()
rl_trader = ReinforcementLearning()

# ===========================
# 🚀 FastAPI Setup
# ===========================
app = FastAPI()

# ===========================
# 🚀 API Routes
# ===========================

@app.get("/api/market_data")
async def get_market_data_api():
    logging.debug("Fetching market data for %s", config.TRADE_SYMBOL)
    try:
        data = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        return data
    except Exception as e:
        logging.error("Error fetching market data: %s", str(e))
        raise HTTPException(status_code=500, detail="Error fetching market data")

@app.get("/api/balance")
async def balance():
    logging.debug("Fetching account balance")
    try:
        balance_data = fetcher.fetch_balance()
        return balance_data
    except Exception as e:
        logging.error("Error fetching balance: %s", str(e))
        raise HTTPException(status_code=500, detail="Error fetching balance")

@app.get("/api/ai/signal")
async def ai_signal(model_type: str = 'ai'):
    """
    Get trading signal using the specified AI model type ('ai' for TradingAI, 'rl' for ReinforcementLearning)
    """
    try:
        # Fetch the market data
        market_data = fetcher.fetch_ohlcv_array(window=60)  # Ensure this returns a (60, 5) array
        market_data = np.expand_dims(market_data, axis=0)  # Add batch dimension
        
        # Choose the model based on the query parameter
        if model_type == 'rl':
            action = rl_trader.predict(market_data)
            logging.debug("AI predicted action (RL): %s", action)
        else:
            action = ai_trader.predict_action(market_data)
            logging.debug("AI predicted action (TradingAI): %s", action)

        return {"action": action}
    except Exception as e:
        logging.error("Error getting AI prediction: %s", str(e))
        raise HTTPException(status_code=500, detail="AI prediction error")

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
        msg=request.body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(received_sig, computed_sig):
        logging.warning("🚫 Webhook signature mismatch!")
        return False
    return True

@app.post("/webhook")
async def webhook_listener(request: Request):
    if not verify_webhook_signature(request):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = await request.json()
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

    return {"status": "Webhook received"}

def notify_team(message):
    logging.info(f"📣 Team Notification: {message}")

# ===========================
# ⏰ Background Trading Job
# ===========================
def run_trading_job():
    logging.info("⏰ Running scheduled trading job...")
    try:
        market_data = fetcher.fetch_ohlcv_array(window=60)
        market_data = np.expand_dims(market_data, axis=0)
        
        # AI Model Decision (can choose TradingAI or ReinforcementLearning)
        ai_action = ai_trader.predict_action(market_data)  # Default to TradingAI
        logging.info(f"📊 AI Action (TradingAI): {ai_action}")

        # Or if you'd like to use the RL model:
        # ai_action = rl_trader.predict(market_data)
        # logging.info(f"📊 AI Action (RL): {ai_action}")

        if ai_action == "buy" or ai_action == "sell":
            balance = fetcher.fetch_balance()["available"]
            position_size = ai_trader.calculate_position_size(balance)
            execute_order(symbol=config.TRADE_SYMBOL, side=ai_action, quantity=position_size)
            logging.info(f"✅ Executed {ai_action.upper()} for {position_size} {config.TRADE_SYMBOL}")
        else:
            logging.info("🤖 AI suggested to hold. No action taken.")

    except Exception as e:
        logging.error("Error in scheduled trading job: %s", str(e))

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ===========================
# 💓 Health Check Endpoint
# ===========================
@app.get("/health")
async def health_check():
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

        return health_data
    except Exception as e:
        logging.error("Health check failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# ===========================
# 🏁 Start App
# ===========================
if __name__ == '__main__':
    import uvicorn
    logging.info("🚀 Starting FastAPI App")
    uvicorn.run(app, host="0.0.0.0", port=5000, debug=True)
