import os
import sys
import json
import logging
import contextlib
from io import StringIO
import hmac
import hashlib
import random
import atexit
import numpy as np

from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client

# Disable GPU and TensorFlow logs
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

with contextlib.redirect_stderr(StringIO()):
    import tensorflow as tf

# --- Internal imports ---
sys.path.append('/app/backend')
from backend.data import DataFetcher, get_market_data
from backend.trading_logic.order_execution import OrderExecution
from backend.ai_models import TradingAI, ReinforcementLearning

# --- Configuration ---
class Config:
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'defaultsecret')

config = Config()

# --- Logging ---
logging.basicConfig(level=logging.DEBUG)

# --- Binance Client ---
if not config.API_KEY or not config.API_SECRET:
    logging.error("Missing Binance API keys in environment!")
    raise ValueError("API_KEY or API_SECRET not found.")

client = Client(config.API_KEY, config.API_SECRET)

# --- Initialize core components ---
fetcher = DataFetcher(api_key=config.API_KEY, api_secret=config.API_SECRET, trade_symbol=config.TRADE_SYMBOL)
order_executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)
ai_trader = TradingAI()
rl_trader = ReinforcementLearning()

# --- FastAPI App ---
app = FastAPI()

# Static frontend assets
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")

@app.get("/api/market_data")
async def get_market_data_api():
    try:
        return get_market_data(config.API_KEY, config.API_SECRET, config.TRADE_SYMBOL)
    except Exception as e:
        logging.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching market data")

@app.get("/api/ai/signal")
async def ai_signal(model_type: str = 'ai'):
    try:
        market_data = np.expand_dims(fetcher.fetch_ohlcv_array(window=60), axis=0)

        if model_type == 'rl':
            action = rl_trader.predict(market_data)
        else:
            action = ai_trader.predict_action(market_data)

        if not action:
            logging.warning("AI returned empty action, defaulting to 'hold'")
            action = "hold"

        logging.debug(f"Predicted action: {action}")
        return {"action": action}
    except Exception as e:
        logging.error(f"AI signal error: {str(e)}")
        return {"action": "hold"}

@app.post("/api/order")
async def place_order(order: dict = Body(...)):
    try:
        side = order.get("side")
        amount = float(order.get("amount"))
        order_type = order.get("type")

        if side not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid side")

        if side == "buy":
            response = client.order_market_buy(symbol=config.TRADE_SYMBOL, quantity=amount)
        else:
            response = client.order_market_sell(symbol=config.TRADE_SYMBOL, quantity=amount)

        logging.info(f"Order placed: {side.upper()} {amount}")
        return {"status": f"{side.capitalize()} order executed", "order": response}
    except Exception as e:
        logging.error(f"Order error: {str(e)}")
        raise HTTPException(status_code=500, detail="Order failed")

@app.post("/api/emergency_stop")
async def emergency_stop():
    logging.warning("Emergency stop activated!")
    return {"status": "Emergency stop triggered"}

@app.get("/health")
async def health_check():
    try:
        client.ping()
        fetcher.fetch_ticker(config.TRADE_SYMBOL)
        return {"status": "healthy", "message": "All systems go", "binance": "connected"}
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="System not healthy")

@app.post("/api/ai/chat")
async def ai_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    logging.info(f"Chat message: {message}")
    response = f"I received your message: '{message}'"
    return {"response": response}

def verify_webhook_signature(request: Request, body: bytes):
    received_sig = request.headers.get('X-Signature')
    if not received_sig:
        return False
    computed_sig = hmac.new(
        key=config.WEBHOOK_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(received_sig, computed_sig)

@app.post("/webhook")
async def webhook_listener(request: Request):
    body = await request.body()
    if not verify_webhook_signature(request, body):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = json.loads(body)
    logging.info(f"Webhook event: {event}")
    return {"status": "Webhook received"}

def notify_team(msg):
    logging.info(f"Notification: {msg}")

def run_trading_job():
    try:
        data = np.expand_dims(fetcher.fetch_ohlcv_array(window=60), axis=0)
        action = ai_trader.predict_action(data)
        if action in ["buy", "sell"]:
            balance = fetcher.fetch_balance().get("available", 0.01)
            qty = ai_trader.calculate_position_size(balance)
            order_executor.execute_order(symbol=config.TRADE_SYMBOL, side=action, quantity=qty)  # Fixed
            logging.info(f"Executed {action.upper()} for {qty}")
        else:
            logging.info("AI suggested HOLD. No action taken.")
    except Exception as e:
        logging.error(f"Scheduled trading error: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=300)
scheduler.start()
atexit.register(scheduler.shutdown)

# --- No need to run Uvicorn directly as Gunicorn will handle the app ---
