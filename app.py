import os
import sys
import json
import logging
import atexit
import random
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client
import openai
from sklearn.metrics import mean_squared_error

# Internal imports
from backend import (
    DataFetcher,
    get_market_data,
    OrderExecution,
    LSTMTradingModel,
    TradingAI,
    ReinforcementLearning,
    get_safe_position_size
)

# Initialize FastAPI app
app = FastAPI()

# Configuration class
class Config:
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'defaultsecret')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

config = Config()
openai.api_key = config.OPENAI_API_KEY

logging.basicConfig(level=logging.DEBUG)

if not config.API_KEY or not config.API_SECRET:
    logging.error("Missing Binance API keys in environment!")
    raise ValueError("API_KEY or API_SECRET not found.")

# Instantiate services
client = Client(config.API_KEY, config.API_SECRET)
fetcher = DataFetcher(api_key=config.API_KEY, api_secret=config.API_SECRET, trade_symbol=config.TRADE_SYMBOL)
order_executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)
lstm_model = LSTMTradingModel(time_steps=10, n_features=10)
trading_ai = TradingAI(api_key=config.API_KEY, api_secret=config.API_SECRET)
reinforcement_model = ReinforcementLearning(config.API_KEY, config.API_SECRET)

# Initialize data
df_data = pd.DataFrame(columns=[
    "open", "high", "low", "close", "volume",
    "rsi", "macd", "sma", "ema", "volatility", "target"
])

# Static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")


@app.get("/api/market_data")
async def get_market_data_api():
    try:
        ticker = fetcher.fetch_ticker(fetcher.trade_symbol)
        simulated_price = ticker.get("price", round(random.uniform(54000, 56000), 2))
        return {
            "symbol": fetcher.trade_symbol,
            "price": simulated_price,
            "time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logging.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching market data")


@app.on_event("startup")
async def train_on_startup():
    global df_data
    for _ in range(50):
        row = {
            "open": 30000.5, "high": 30200.2, "low": 29900.1, "close": 30100.6,
            "volume": 105.23, "rsi": 55.2, "macd": 0.3, "sma": 30120.1,
            "ema": 30090.7, "volatility": 0.005, "target": 30150.0
        }
        df_data = pd.concat([df_data, pd.DataFrame([row])], ignore_index=True)

    if len(df_data) > lstm_model.time_steps:
        lstm_model.train(df_data.drop(columns=['target']).values, df_data['target'].values)


def check_model_drift(features, actual_price):
    predictions = {
        "lstm": lstm_model.predict(features),
        "trading_ai": trading_ai.predict(features),
        "rl": reinforcement_model.predict(features)
    }
    mse = {model: mean_squared_error([actual_price], pred) for model, pred in predictions.items()}
    drift_threshold = 100
    for model, error in mse.items():
        if error > drift_threshold:
            logging.warning(f"{model} model drift detected with error {error:.2f}. Consider retraining.")
            return True
    return False


def process_and_execute_trade(new_data, models_to_use=None, confidence_threshold=50):
    global df_data
    df_data = pd.concat([df_data, pd.DataFrame([new_data])], ignore_index=True)

    if len(df_data) <= lstm_model.time_steps:
        return {"message": "Not enough data yet"}, 400

    features = df_data.drop(columns=['target']).values

    if check_model_drift(features, new_data["close"]):
        return {"message": "Model drift detected, consider retraining models."}, 500

    predictions = {}
    if models_to_use is None:
        models_to_use = ["lstm", "trading_ai", "rl"]

    if "lstm" in models_to_use:
        predictions["lstm"] = lstm_model.predict(features)[0][0]
    if "trading_ai" in models_to_use:
        predictions["trading_ai"] = trading_ai.predict(features)[0][0]
    if "rl" in models_to_use:
        predictions["rl"] = reinforcement_model.predict(features)[0][0]

    final_predicted_price = sum(predictions.values()) / len(predictions)
    actual_price = new_data["close"]
    confidence = abs(final_predicted_price - actual_price)

    if confidence < confidence_threshold:
        return {
            "message": f"Confidence ({confidence:.2f}) below threshold ({confidence_threshold}). No trade executed."
        }, 200

    action = "buy" if final_predicted_price > actual_price else "sell"
    balance = fetcher.fetch_balance().get("available", 1000)
    qty = get_safe_position_size(balance)

    order_executor.execute_trade(config.TRADE_SYMBOL, action, qty)

    return {
        "action": action,
        "final_predicted_price": final_predicted_price,
        "actual_price": actual_price,
        "confidence": confidence,
        **predictions
    }, 200


@app.post("/api/auto_trade")
async def auto_trade():
    new_data = {
        "open": 30000.6, "high": 30210.0, "low": 29920.0, "close": 30120.0,
        "volume": 105.75, "rsi": 55.5, "macd": 0.4, "sma": 30130.0,
        "ema": 30095.5, "volatility": 0.006, "target": 30180.0
    }
    result, status = process_and_execute_trade(new_data)
    return JSONResponse(content=result, status_code=status)


def run_trading_job():
    try:
        symbol = fetcher.trade_symbol
        new_data = fetcher.fetch_ticker(symbol)
        models_to_use = ["lstm", "trading_ai", "rl"]
        confidence_threshold = 50

        result, status = process_and_execute_trade(
            new_data,
            models_to_use=models_to_use,
            confidence_threshold=confidence_threshold
        )

        if status == 200 and "action" in result:
            logging.info(f"Scheduled trade: Executed {result['action'].upper()} order at {result['final_predicted_price']}")
        else:
            logging.info(f"Scheduled trade skipped: {result.get('message')}")
    except Exception as e:
        logging.error(f"Scheduled trading error: {str(e)}")


# Schedule the trading job
scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=300)
scheduler.start()
atexit.register(scheduler.shutdown)


@app.post("/api/emergency_stop")
async def emergency_stop():
    logging.warning("Emergency stop activated!")
    return {"status": "Emergency stop triggered"}


@app.get("/health")
async def health_check():
    try:
        client.ping()
        fetcher.fetch_ticker(fetcher.trade_symbol)
        return {"status": "healthy", "message": "All systems go", "binance": "connected"}
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="System not healthy")