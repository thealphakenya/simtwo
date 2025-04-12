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

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Config
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.01
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'dev_webhook')

if not API_KEY or not API_SECRET:
    logger.warning("Missing API key or secret.")

class Config:
    API_KEY = API_KEY
    API_SECRET = API_SECRET
    TRADE_SYMBOL = TRADE_SYMBOL
    TRADE_QUANTITY = TRADE_QUANTITY
    WEBHOOK_SECRET = WEBHOOK_SECRET
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

config = Config()
openai.api_key = config.OPENAI_API_KEY

# App Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

client = Client(config.API_KEY, config.API_SECRET)
fetcher = DataFetcher(config.API_KEY, config.API_SECRET, config.TRADE_SYMBOL)
order_executor = OrderExecution(config.API_KEY, config.API_SECRET)

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
use_virtual_account = True
virtual_balance = 200.00

# AI Status System
ai_status = {
    "state": "LOADING",
    "details": "System booting up"
}

def update_ai_status(state: str, details: str = ""):
    ai_status["state"] = state
    ai_status["details"] = details or state

update_ai_status("LOADING", "System booting up and loading models")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")

@app.get("/api/market_data")
async def get_market_data_api():
    try:
        data = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        update_ai_status("ACTIVE", "Monitoring market conditions")
        return data
    except Exception as e:
        update_ai_status("ERROR", "Failed to fetch market data")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai_status")
async def get_ai_status():
    return {
        "status": f"{ai_status['state']} - {ai_status['details']}"
    }

@app.post("/api/set_ai_status")
async def set_ai_status(request: Request):
    try:
        data = await request.json()
        status = data.get("status")
        details = data.get("details", "")
        if status not in ["ACTIVE", "STOPPED"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        update_ai_status(status, details)
        return {"status": "AI status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/balance")
async def get_balance():
    try:
        if use_virtual_account:
            update_ai_status("VIRTUAL MODE", "Running in virtual test account mode")
            return {"balance": round(virtual_balance, 2), "account": "virtual"}
        else:
            account = client.get_asset_balance(asset="USDT")
            update_ai_status("ACTIVE", "Monitoring real account")
            return {"balance": float(account['free']), "account": "real"}
    except Exception as e:
        update_ai_status("ERROR", "Balance fetch failed")
        raise HTTPException(status_code=500, detail="Balance fetch failed")

@app.post("/api/set_preferences")
async def set_preferences(request: Request):
    global ai_managed_preferences, auto_trade_enabled, use_virtual_account
    data = await request.json()
    ai_managed_preferences = data.get("ai_managed_preferences", ai_managed_preferences)
    auto_trade_enabled = data.get("auto_trade_enabled", auto_trade_enabled)
    use_virtual_account = data.get("virtual", use_virtual_account)
    update_ai_status("UPDATING", "Preferences updated by user")
    return {
        "status": "Preferences updated",
        "ai_managed_preferences": ai_managed_preferences,
        "auto_trade_enabled": auto_trade_enabled,
        "account_mode": "virtual" if use_virtual_account else "real"
    }

@app.post("/api/auto_trade")
async def auto_trade(request: Request):
    try:
        data = await request.json()
        model_type = data.get("model", "ensemble")
        confidence = float(data.get("confidence_threshold", 0.5))

        update_ai_status("ACTIVE", "Trading decision in progress")

        if model_type == "lstm":
            prediction = lstm_model.predict(df_data)
        elif model_type == "trading_ai":
            prediction = trading_ai.predict(df_data)
        elif model_type == "rl":
            prediction = reinforcement_model.predict(df_data)
        else:
            pred_lstm = lstm_model.predict(df_data)
            pred_ai = trading_ai.predict(df_data)
            pred_rl = reinforcement_model.predict(df_data)
            prediction = np.mean([pred_lstm, pred_ai, pred_rl])

        action = "buy" if prediction > confidence else "sell"

        update_ai_status("ACTIVE", f"Monitoring... Last decision: {action.upper()}")
        return {"final_predicted_price": float(prediction), "action": action}
    except Exception as e:
        update_ai_status("ERROR", "Auto trade failed")
        raise HTTPException(status_code=500, detail="Auto trade failed")

@app.post("/api/order")
async def place_order(request: Request):
    global virtual_balance
    try:
        body = await request.json()
        side = body["side"]
        order_type = body.get("type", "market")
        quantity = float(body["amount"])

        update_ai_status("ACTIVE", "Placing order...")

        if use_virtual_account:
            if side == "buy":
                virtual_balance -= quantity * 100
            else:
                virtual_balance += quantity * 100
            update_ai_status("VIRTUAL MODE", "Virtual order executed")
            return {"status": "virtual order executed", "balance": round(virtual_balance, 2)}

        else:
            result = order_executor.place_market_order(
                symbol=config.TRADE_SYMBOL,
                side=side.upper(),
                quantity=quantity
            )
            update_ai_status("ACTIVE", "Real order executed")
            return {"status": "real order executed", "order": result}
    except Exception as e:
        update_ai_status("ERROR", "Order failed")
        raise HTTPException(status_code=500, detail="Order failed")

@app.post("/api/emergency_stop")
async def emergency_stop():
    scheduler.pause()
    update_ai_status("EMERGENCY STOP", "Trading halted by emergency trigger")
    return {"status": "Emergency stop triggered"}

@app.post("/api/ai/chat")
async def chat_with_ai(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        if not user_input:
            raise ValueError("Message is empty")

        update_ai_status("STANDBY", "Responding to AI query")

        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=user_input,
            max_tokens=150
        )

        update_ai_status("ACTIVE", "Monitoring...")
        return {"response": response.choices[0].text.strip()}
    except Exception as e:
        update_ai_status("ERROR", "AI chat failed")
        logger.error(f"AI chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI chat failed")

@app.get("/health")
async def health_check():
    try:
        client.ping()
        fetcher.fetch_ticker(config.TRADE_SYMBOL)
        update_ai_status("ACTIVE", "System healthy and monitoring")
        return {"status": "healthy"}
    except Exception as e:
        update_ai_status("ERROR", "Health check failed")
        raise HTTPException(status_code=500, detail="System not healthy")

@app.post("/webhook")
async def webhook_listener(request: Request, x_signature: str = Header(None)):
    body = await request.body()
    request._body = body
    if not verify_webhook_signature(request, x_signature):
        update_ai_status("ERROR", "Webhook signature mismatch")
        raise HTTPException(status_code=401, detail="Invalid signature")

    update_ai_status("UPDATING", "Webhook received")
    return {"status": "Webhook received"}

def verify_webhook_signature(request: Request, x_signature: str) -> bool:
    raw_body = request._body
    computed_sig = hmac.new(
        key=config.WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(x_signature, computed_sig)

# Background Job
def run_trading_job():
    try:
        ticker = fetcher.fetch_ticker(config.TRADE_SYMBOL)
        logger.info(f"Scheduled fetch: {ticker}")
        update_ai_status("ACTIVE", "Monitoring via scheduled fetch")
    except Exception as e:
        update_ai_status("ERROR", "Scheduled job failed")
        logger.error(f"Job failed: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger="interval", seconds=300)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())