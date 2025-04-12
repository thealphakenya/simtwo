import os
import sys
import json
import logging
import hmac
import hashlib
import atexit
import asyncio
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Header, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import openai
import numpy as np
import pandas as pd
import httpx
from binance.client import Client
from starlette.websockets import WebSocketState

# Local modules
from backend import (
    DataFetcher,
    get_market_data,
    OrderExecution,
    LSTMTradingModel,
    TradingAI,
    ReinforcementLearning,
    get_safe_position_size
)
from memory_manager import (
    append_conversation,
    reset_memory,
    load_memory,
    update_strategy_weights,
    get_strategy_weights
)

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'dev_webhook')
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.01
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

# App setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Binance and backend logic
client = Client(API_KEY, API_SECRET)
fetcher = DataFetcher(API_KEY, API_SECRET, TRADE_SYMBOL)
order_executor = OrderExecution(API_KEY, API_SECRET)
lstm_model = LSTMTradingModel(time_steps=10, n_features=10)
trading_ai = TradingAI(API_KEY, API_SECRET)
reinforcement_model = ReinforcementLearning(API_KEY, API_SECRET)

# In-memory state
df_data = pd.DataFrame(columns=[
    "open", "high", "low", "close", "volume",
    "rsi", "macd", "sma", "ema", "volatility", "target"
])
ai_managed_preferences = True
auto_trade_enabled = False
use_virtual_account = True
virtual_balance = 200.00

ai_status = {
    "state": "LOADING",
    "details": "System booting up"
}

def update_ai_status(state: str, details: str = ""):
    ai_status["state"] = state
    ai_status["details"] = details or state

update_ai_status("LOADING", "System booting up and loading models")

# WebSocket connections
active_connections = set()

async def broadcast_chart_data():
    while True:
        try:
            chart_data = fetcher.fetch_chart_data(TRADE_SYMBOL, interval='1m', limit=20)
            payload = [{"time": item["timestamp"], "price": item["close"]} for item in chart_data]
            message = json.dumps(payload)
            for ws in list(active_connections):
                if ws.application_state == WebSocketState.CONNECTED:
                    await ws.send_text(message)
        except Exception as e:
            logger.error(f"WebSocket broadcast error: {str(e)}")
        await asyncio.sleep(5)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("WebSocket client connected.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
        active_connections.remove(websocket)

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")

# Market data from Binance (new endpoint preserved)
@app.get("/api/live_market_data")
async def market_data(symbol: str = Query(default="BTCUSDT", description="Binance trading pair e.g., BTCUSDT")):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        return {
            "symbol": data["symbol"],
            "price": float(data["price"]),
            "source": "binance"
        }
    except httpx.HTTPStatusError as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to fetch from Binance: {e.response.text}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})

# All other API endpoints
@app.get("/api/memory")
async def get_memory():
    return load_memory()

@app.post("/api/memory/reset")
async def reset_user_memory():
    reset_memory()
    return {"status": "Memory reset"}

@app.get("/api/ai_status")
async def get_ai_status():
    return {"status": f"{ai_status['state']} - {ai_status['details']}"}

@app.post("/api/set_ai_status")
async def set_ai_status(request: Request):
    data = await request.json()
    status = data.get("status")
    details = data.get("details", "")
    if status not in ["ACTIVE", "STOPPED"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    update_ai_status(status, details)
    return {"status": "AI status updated"}

@app.get("/api/balance")
async def get_balance():
    try:
        if use_virtual_account:
            update_ai_status("VIRTUAL MODE", "Running in virtual test account mode")
            return {"balance": round(virtual_balance, 2), "account": "virtual"}
        else:
            account = client.get_asset_balance(asset="USDT")
            return {"balance": float(account['free']), "account": "real"}
    except Exception:
        raise HTTPException(status_code=500, detail="Balance fetch failed")

@app.get("/api/market_data")
async def get_market_data_api():
    try:
        data = fetcher.fetch_ticker(TRADE_SYMBOL)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart_data")
async def get_chart_data():
    try:
        chart_data = fetcher.fetch_chart_data(TRADE_SYMBOL, interval='1m', limit=20)
        return [{"time": item["timestamp"], "price": item["close"]} for item in chart_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/set_preferences")
async def set_preferences(request: Request):
    global ai_managed_preferences, auto_trade_enabled, use_virtual_account
    data = await request.json()
    ai_managed_preferences = data.get("ai_managed_preferences", ai_managed_preferences)
    auto_trade_enabled = data.get("auto_trade_enabled", auto_trade_enabled)
    use_virtual_account = data.get("virtual", use_virtual_account)
    return {
        "status": "Preferences updated",
        "ai_managed_preferences": ai_managed_preferences,
        "auto_trade_enabled": auto_trade_enabled,
        "account_mode": "virtual" if use_virtual_account else "real"
    }

@app.post("/api/auto_trade")
async def auto_trade(request: Request):
    data = await request.json()
    model_type = data.get("model", "ensemble")
    confidence = float(data.get("confidence_threshold", 0.5))

    if model_type == "lstm":
        prediction = lstm_model.predict(df_data)
    elif model_type == "trading_ai":
        prediction = trading_ai.predict(df_data)
    elif model_type == "rl":
        prediction = reinforcement_model.predict(df_data)
    else:
        prediction = np.mean([
            lstm_model.predict(df_data),
            trading_ai.predict(df_data),
            reinforcement_model.predict(df_data)
        ])

    action = "buy" if prediction > confidence else "sell"
    return {"final_predicted_price": float(prediction), "action": action}

@app.post("/api/order")
async def place_order(request: Request):
    global virtual_balance
    body = await request.json()
    side = body["side"]
    order_type = body.get("type", "market")
    quantity = float(body["amount"])

    if use_virtual_account:
        if side == "buy":
            virtual_balance -= quantity * 100
        else:
            virtual_balance += quantity * 100
        return {"status": "virtual order executed", "balance": round(virtual_balance, 2)}
    else:
        result = order_executor.place_market_order(
            symbol=TRADE_SYMBOL,
            side=side.upper(),
            quantity=quantity
        )
        return {"status": "real order executed", "order": result}

@app.post("/api/emergency_stop")
async def emergency_stop():
    scheduler.pause()
    update_ai_status("EMERGENCY STOP", "Trading halted")
    return {"status": "Emergency stop triggered"}

@app.post("/api/ai/chat")
async def chat_with_ai(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    response = openai.Completion.create(
        model="gpt-4",
        prompt=user_input,
        max_tokens=150
    )
    reply = response.choices[0].text.strip()
    append_conversation(user_input, reply)
    return {"response": reply}

@app.post("/api/strategy_weights")
async def set_strategy_weights(request: Request):
    data = await request.json()
    update_strategy_weights(data)
    return {"status": "Strategy weights updated"}

@app.get("/api/strategy_weights")
async def get_strategy_weights_api():
    return get_strategy_weights()

@app.get("/health")
async def health_check():
    try:
        client.ping()
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=500, detail="Unhealthy")

@app.post("/webhook")
async def webhook_listener(request: Request, x_signature: str = Header(None)):
    body = await request.body()
    request._body = body
    if not verify_webhook_signature(request, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return {"status": "Webhook received"}

def verify_webhook_signature(request: Request, x_signature: str) -> bool:
    raw_body = request._body
    computed_sig = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(x_signature, computed_sig)

# Scheduler
def run_trading_job():
    try:
        ticker = fetcher.fetch_ticker(TRADE_SYMBOL)
        logger.info(f"Scheduled fetch: {ticker}")
    except Exception as e:
        logger.error(f"Job failed: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger="interval", seconds=300)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_chart_data())