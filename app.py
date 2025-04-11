import os
import sys
import json
import logging
import hmac
import hashlib
import atexit
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client
import openai
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv

# Backend Modules
from backend import (
    DataFetcher,
    get_market_data,
    OrderExecution,
    LSTMTradingModel,
    TradingAI,
    ReinforcementLearning,
    get_safe_position_size
)

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ===========================
# 🔐 Pre-Config Check
# ===========================
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.01
WEBHOOK_SECRET = 'd9f1a3d47f83e25f92c97a912b3ac31c45ff98c87e2e98b03d78a12a78a813f5'

# Log API keys to verify if they're loaded correctly
if not API_KEY or not API_SECRET:
    logger.error("API Key or Secret is missing!")
else:
    logger.debug(f"API Key Loaded: Yes, API Secret Loaded: Yes")

# ===========================
# 📦 Configuration
# ===========================
class Config:
    API_KEY = API_KEY
    API_SECRET = API_SECRET
    TRADE_SYMBOL = TRADE_SYMBOL
    TRADE_QUANTITY = TRADE_QUANTITY
    WEBHOOK_SECRET = WEBHOOK_SECRET
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

config = Config()
openai.api_key = config.OPENAI_API_KEY

# FastAPI App Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Log config values (omit actual secrets in logs)
logger.debug(f"Config Loaded: TRADE_SYMBOL={config.TRADE_SYMBOL}, TRADE_QUANTITY={config.TRADE_QUANTITY}")
logger.debug(f"API Key Loaded: {'Yes' if config.API_KEY else 'No'}, Secret Loaded: {'Yes' if config.API_SECRET else 'No'}")

# Init Binance & Trading Components
try:
    client = Client(config.API_KEY, config.API_SECRET)
    fetcher = DataFetcher(config.API_KEY, config.API_SECRET, config.TRADE_SYMBOL)
    order_executor = OrderExecution(config.API_KEY, config.API_SECRET)
except Exception as e:
    logger.error(f"Error initializing Binance Client: {str(e)}")
    raise

# Models
lstm_model = LSTMTradingModel(time_steps=10, n_features=10)
trading_ai = TradingAI(config.API_KEY, config.API_SECRET)
reinforcement_model = ReinforcementLearning(config.API_KEY, config.API_SECRET)

# Global State
df_data = pd.DataFrame(columns=[
    "open", "high", "low", "close", "volume",
    "rsi", "macd", "sma", "ema", "volatility", "target"
])
ai_managed_preferences = True
auto_trade_enabled = False

# Home Route
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")

# Market Data
@app.get("/api/market_data")
async def get_market_data_api():
    try:
        data = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        return data
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook Signature Verification
def verify_webhook_signature(request: Request, x_signature: str) -> bool:
    raw_body = request._body
    computed_sig = hmac.new(
        key=config.WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(x_signature, computed_sig)

@app.post("/webhook")
async def webhook_listener(request: Request, x_signature: str = Header(None)):
    if not x_signature:
        logger.warning("Missing signature in webhook")
        raise HTTPException(status_code=401, detail="Missing signature")
    body = await request.body()
    request._body = body  # Store raw body for signature

    if not verify_webhook_signature(request, x_signature):
        logger.warning("Webhook signature mismatch")
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = json.loads(body)
    logger.info(f"Webhook Event: {event}")

    return {"status": "Webhook received"}

# AI Prediction (stubbed)
@app.post("/api/ai_predict")
async def ai_predict(request: Request):
    try:
        market_data = await request.json()
        if ai_managed_preferences:
            prediction = reinforcement_model.predict(market_data)
        else:
            prediction = trading_ai.predict(market_data)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        logger.error(f"AI prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI prediction failed")

# Preferences
@app.post("/api/set_preferences")
async def set_preferences(request: Request):
    global ai_managed_preferences, auto_trade_enabled
    data = await request.json()
    ai_managed_preferences = data.get('ai_managed_preferences', ai_managed_preferences)
    auto_trade_enabled = data.get('auto_trade_enabled', auto_trade_enabled)
    logger.info(f"Preferences updated: AI={ai_managed_preferences}, Auto={auto_trade_enabled}")
    return {"status": "Preferences updated", "ai_managed_preferences": ai_managed_preferences, "auto_trade_enabled": auto_trade_enabled}

# Emergency Stop
@app.post("/api/emergency_stop")
async def emergency_stop():
    logger.warning("Emergency stop activated!")
    scheduler.pause()
    return {"status": "Emergency stop triggered"}

# Health Check
@app.get("/health")
async def health_check():
    try:
        client.ping()
        fetcher.fetch_ticker(config.TRADE_SYMBOL)
        return {"status": "healthy", "message": "All systems go", "binance": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="System not healthy")

# Trading Job
def run_trading_job():
    logger.info("Scheduled job: Checking market")
    try:
        ticker = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        logger.debug(f"Fetched ticker: {ticker}")
        # Add actual trading logic here
    except Exception as e:
        logger.error(f"Trading job error: {str(e)}")

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=300)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())