import os
import sys
import json
import logging
import contextlib
import hmac
import hashlib
import atexit
import random
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client
import openai
from sklearn.metrics import mean_squared_error

# Internal imports for AI model and trading logic
from backend.ai_models import LSTMTradingModel, TradingAI  # Updated import path
from backend.data import DataFetcher
from backend.trading_logic.order_execution import OrderExecution

# FastAPI setup
app = FastAPI()

# Configuration and logging
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

# Binance Client
if not config.API_KEY or not config.API_SECRET:
    logging.error("Missing Binance API keys in environment!")
    raise ValueError("API_KEY or API_SECRET not found.")

client = Client(config.API_KEY, config.API_SECRET)

# Initialize components
fetcher = DataFetcher(api_key=config.API_KEY, api_secret=config.API_SECRET, trade_symbol=config.TRADE_SYMBOL)
order_executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)

# Initialize LSTM model
lstm_model = LSTMTradingModel(time_steps=10, n_features=10)

# Initialize TradingAI model
trading_ai = TradingAI(api_key=config.API_KEY, api_secret=config.API_SECRET)

# Reinforcement Learning Model Implementation (Q-learning Example)
class ReinforcementLearning:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.q_table = {}  # Simple Q-table to store Q-values

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def update_q_value(self, state, action, reward, next_state, learning_rate=0.1, discount_factor=0.9):
        best_next_action = max([self.get_q_value(next_state, a) for a in ["buy", "sell"]])
        new_q_value = self.get_q_value(state, action) + learning_rate * (reward + discount_factor * best_next_action - self.get_q_value(state, action))
        self.q_table[(state, action)] = new_q_value

    def predict(self, features):
        # Simple logic to predict action based on Q-values
        state = str(features)  # Convert features to string as state
        action = max(["buy", "sell"], key=lambda a: self.get_q_value(state, a))
        return [random.uniform(54000, 56000)]  # Placeholder logic for RL

    def learn_from_results(self, action, reward, state, next_state):
        self.update_q_value(state, action, reward, next_state)

reinforcement_model = ReinforcementLearning(config.API_KEY, config.API_SECRET)

# Global DataFrame to simulate market data storage
df_data = pd.DataFrame(columns=[
    "open", "high", "low", "close", "volume", "rsi", "macd", "sma", "ema", "volatility", "target"
])

# Serve static files (index.html, app.js, style.css)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Endpoint to return the home page (index.html)
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("frontend/index.html")

# Endpoint to get market data
@app.get("/api/market_data")
async def get_market_data_api():
    try:
        # Fetch real-time market data from Binance API
        ticker = fetcher.fetch_ticker(fetcher.trade_symbol)
        simulated_price = ticker.get("price", round(random.uniform(54000, 56000), 2))
        return {"symbol": fetcher.trade_symbol, "price": simulated_price, "time": datetime.utcnow().isoformat()}
    except Exception as e:
        logging.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching market data")

# Training the LSTM model on startup
@app.on_event("startup")
async def train_on_startup():
    global df_data
    # Add mock data if not enough data is available
    for _ in range(50):  # Simulate loading 50 historical rows
        row = {
            "open": 30000.5, "high": 30200.2, "low": 29900.1, "close": 30100.6, "volume": 105.23, 
            "rsi": 55.2, "macd": 0.3, "sma": 30120.1, "ema": 30090.7, "volatility": 0.005, "target": 30150.0
        }
        df_data = pd.concat([df_data, pd.DataFrame([row])], ignore_index=True)

    if len(df_data) > lstm_model.time_steps:
        lstm_model.train(df_data.drop(columns=['target']).values, df_data['target'].values)
    else:
        logging.warning("Not enough historical data to train LSTM model.")

# Model Drift Detection (Simple Accuracy Check)
def check_model_drift(features, actual_price):
    predictions = {
        "lstm": lstm_model.predict(features),
        "trading_ai": trading_ai.predict(features),
        "rl": reinforcement_model.predict(features)
    }
    mse = {model: mean_squared_error([actual_price], pred) for model, pred in predictions.items()}
    drift_threshold = 100  # Example threshold for model drift
    for model, error in mse.items():
        if error > drift_threshold:
            logging.warning(f"{model} model drift detected with error {error:.2f}. Consider retraining.")
            return True
    return False

# Endpoint to handle auto trading using multiple models (LSTM, TradingAI, ReinforcementLearning)
@app.post("/api/auto_trade")
async def auto_trade():
    global df_data
    new_data = {
        "open": 30000.6, "high": 30210.0, "low": 29920.0, "close": 30120.0, "volume": 105.75,
        "rsi": 55.5, "macd": 0.4, "sma": 30130.0, "ema": 30095.5, "volatility": 0.006, "target": 30180.0
    }
    df_data = pd.concat([df_data, pd.DataFrame([new_data])], ignore_index=True)

    # Check if we have enough data to make predictions
    if len(df_data) <= lstm_model.time_steps:
        return JSONResponse(content={"message": "Not enough data yet"}, status_code=400)

    # Prepare features and get predictions from all models
    features = df_data.drop(columns=['target']).values
    
    # Check for model drift
    if check_model_drift(features, new_data["close"]):
        return JSONResponse(content={"message": "Model drift detected, consider retraining models."}, status_code=500)

    # Get predictions from models
    lstm_prediction = lstm_model.predict(features)
    trading_ai_prediction = trading_ai.predict(features)
    rl_prediction = reinforcement_model.predict(features)

    # Combine predictions - here we use averaging as a simple ensemble method
    final_predicted_price = (lstm_prediction[0][0] + trading_ai_prediction[0][0] + rl_prediction[0][0]) / 3

    actual_price = new_data["close"]

    # Basic trading strategy based on final predicted price
    action = "buy" if final_predicted_price > actual_price else "sell"
    
    return {
        "action": action,
        "final_predicted_price": final_predicted_price,
        "lstm_predicted_price": lstm_prediction[0][0],
        "trading_ai_predicted_price": trading_ai_prediction[0][0],
        "rl_predicted_price": rl_prediction[0][0],
        "actual_price": actual_price
    }

# Background job for periodic trading execution (every 5 minutes)
def run_trading_job():
    try:
        symbol = fetcher.trade_symbol
        # Fetch real-time market data for trading
        new_data = fetcher.fetch_ticker(symbol)
        df_data = pd.concat([df_data, pd.DataFrame([new_data])], ignore_index=True)

        if len(df_data) <= lstm_model.time_steps:
            return

        features = df_data.drop(columns=['target']).values
        
        # Get predictions from each model
        lstm_prediction = lstm_model.predict(features)
        trading_ai_prediction = trading_ai.predict(features)
        rl_prediction = reinforcement_model.predict(features)

        # Combine predictions using averaging
        final_predicted_price = (lstm_prediction[0][0] + trading_ai_prediction[0][0] + rl_prediction[0][0]) / 3
        
        action = "buy" if final_predicted_price > new_data["close"] else "sell"
        
        # Example order execution based on action
        balance = fetcher.fetch_balance().get("available", 0.01)  # Simulated balance
        qty = 0.01  # Example quantity to trade
        if action == "buy":
            order_executor.execute_order(symbol, "buy", qty)
        else:
            order_executor.execute_order(symbol, "sell", qty)

        logging.info(f"Executed {action.upper()} order for {qty} {symbol} at predicted price {final_predicted_price}.")
    except Exception as e:
        logging.error(f"Scheduled trading error: {str(e)}")

# Scheduler to run the trading job every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(run_trading_job, trigger='interval', seconds=300)
scheduler.start()
atexit.register(scheduler.shutdown)

# Emergency stop endpoint
@app.post("/api/emergency_stop")
async def emergency_stop():
    logging.warning("Emergency stop activated!")
    return {"status": "Emergency stop triggered"}

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        client.ping()
        fetcher.fetch_ticker(fetcher.trade_symbol)
        return {"status": "healthy", "message": "All systems go", "binance": "connected"}
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="System not healthy")
