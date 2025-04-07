import logging
import os
import time
import requests
import psutil
import asyncio
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from binance.client import Client

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# API Key and Secret for Binance
api_key = '3WohOdIVubUyXpqgkLvyNnOMzDwu2rX6jOpp2x53U39bL9gfDIVaTUSIUFIebOoC'
api_secret = 'EOhCwX57bCVqGhThezazN0frWBAPGBN9elIcBH8Ejk91uqPieCBUnYh0dVPdysoA'
binance_client = Client(api_key, api_secret)

# Trading pair and market data
current_pair = "BTCUSDT"

# Initialize Scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()

# Monitor system resources
def monitor_resources():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    logger.info("CPU Usage: %s%%", cpu_usage)
    logger.info("Memory Usage: %s%% (Available: %s MB)", memory_info.percent, memory_info.available / (1024 * 1024))

# Fetch market data
def fetch_market_data():
    try:
        logger.debug("Fetching market data for pair: %s", current_pair)
        avg_price = binance_client.get_avg_price(symbol=current_pair)
        price = avg_price['price']
        logger.debug("Fetched price: %s", price)
        return price
    except Exception as e:
        logger.error("Failed to fetch market data: %s", e, exc_info=True)
        return None

# Periodic job to fetch market data
@scheduler.scheduled_job(IntervalTrigger(seconds=60))
def update_market_data():
    price = fetch_market_data()
    if price:
        socketio.emit('market_data', {'price': price})

# Web route to serve market data
@app.route('/api/market_data', methods=['GET'])
def market_data():
    try:
        price = fetch_market_data()
        if price:
            return jsonify({'prices': [[time.time(), float(price)]]}), 200
        else:
            return jsonify({'error': 'Failed to fetch market data'}), 500
    except Exception as e:
        logger.error("Error fetching market data: %s", e, exc_info=True)
        return jsonify({'error': 'Internal Server Error'}), 500

# WebSocket events
@socketio.on('place_order')
def handle_place_order(data):
    try:
        logger.debug("Placing order: %s", data)
        # Add order placement logic here (buy/sell)
        socketio.emit('order_status', {'status': 'Order placed successfully'})
    except Exception as e:
        logger.error("Error placing order: %s", e, exc_info=True)
        socketio.emit('order_status', {'status': 'Error placing order'})

@socketio.on('emergency_stop')
def handle_emergency_stop(data):
    try:
        logger.info("Emergency stop triggered: %s", data)
        # Handle emergency stop logic (e.g., stop trading)
        socketio.emit('emergency_stop_status', {'status': 'Trading stopped'})
    except Exception as e:
        logger.error("Error during emergency stop: %s", e, exc_info=True)
        socketio.emit('emergency_stop_status', {'status': 'Error stopping trading'})

@socketio.on('chat_message')
def handle_chat_message(data):
    try:
        message = data.get('message')
        logger.info("Received chat message: %s", message)
        # Simulate AI response (this could be more complex, e.g., using GPT-3 or similar)
        response = f"AI: {message[::-1]}"  # Simple reversal of the message for demo purposes
        socketio.emit('ai_response', response)
    except Exception as e:
        logger.error("Error handling chat message: %s", e, exc_info=True)
        socketio.emit('ai_response', "Error handling your message")

@socketio.on('get_ai_status')
def handle_ai_status():
    try:
        logger.debug("Fetching AI status...")
        # Here you could query the AI model's current status
        ai_status = 'active'  # For demo purposes, we assume the AI is always active
        socketio.emit('ai_status', ai_status)
    except Exception as e:
        logger.error("Error fetching AI status: %s", e, exc_info=True)
        socketio.emit('ai_status', 'inactive')

# Frontend route to serve HTML
@app.route('/')
def index():
    return render_template('index.html')

# Error handling (for unexpected crashes)
@app.errorhandler(Exception)
def handle_error(error):
    logger.error("Unexpected error occurred: %s", error, exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask app...")
    try:
        monitor_resources()  # Initial resource monitoring
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error("Error starting Flask app: %s", e, exc_info=True)
