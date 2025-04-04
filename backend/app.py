from flask import Flask, request, jsonify
from binance.client import Client
from ai_models.model import TradingAI, train_model, predict_trade
from trading_logic.order_execution import execute_order
from data.data_fetcher import get_market_data

app = Flask(__name__)

# Binance Client Initialization
binance_api_key = "your_api_key"
binance_api_secret = "your_api_secret"
client = Client(binance_api_key, binance_api_secret)

# AI Models
from ai_models.model import ReinforcementLearning, NeuralNetwork

# Store AI strategy state
ai_managed_preferences = True
auto_trade_enabled = False

# Load the trained model or train a new one
model = None
try:
    model = TradingAI()
    model.load_model('saved_model.h5')  # Try loading an existing model
except:
    print("Model not found. Training new model.")
    # Assuming 'data' is loaded somewhere, like a CSV file with historical data
    # data = pd.read_csv('historical_data.csv')  # Replace with actual data source
    model = train_model(data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Preprocess the input data as required for prediction
    prediction = predict_trade(data, model)
    return jsonify({"prediction": prediction.tolist()})

@app.route('/api/market_data', methods=['GET'])
def get_market_data_api():
    # Get real-time market data (e.g., price, volume)
    data = get_market_data('BTCUSDT')  # Example for BTC/USD pair
    return jsonify(data)

@app.route('/api/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    symbol = order_data['symbol']
    quantity = order_data['quantity']
    order_type = order_data['order_type']
    
    # Execute order via Binance API
    result = execute_order(symbol, quantity, order_type)
    return jsonify(result)

@app.route('/api/ai_predict', methods=['POST'])
def ai_predict():
    market_data = request.json
    # Use the AI model to make predictions based on the market data
    if ai_managed_preferences:
        prediction = ReinforcementLearning().predict(market_data)
    else:
        prediction = NeuralNetwork().predict(market_data)
    return jsonify(prediction)

@app.route('/api/set_preferences', methods=['POST'])
def set_preferences():
    global ai_managed_preferences, auto_trade_enabled
    preferences = request.json
    ai_managed_preferences = preferences.get('ai_managed_preferences', ai_managed_preferences)
    auto_trade_enabled = preferences.get('auto_trade_enabled', auto_trade_enabled)
    return jsonify({"status": "Preferences updated", "ai_managed_preferences": ai_managed_preferences, "auto_trade_enabled": auto_trade_enabled})

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    # Run simulation with the current AI strategy
    results = simulate_trading_strategy()
    return jsonify(results)

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    # Stop all trading actions
    stop_trading()
    return jsonify({"status": "Emergency stop activated"})

def simulate_trading_strategy():
    # Simulate AI strategy
    return {
        "P&L": 1500,
        "Sharpe Ratio": 1.75,
        "Win Rate": 65,
        "Max Drawdown": -10
    }

def stop_trading():
    # Logic to stop all active trades (e.g., cancel orders, stop AI trading)
    pass

if __name__ == '__main__':
    app.run(debug=True)
