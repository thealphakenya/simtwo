# backend/trading_logic/order_execution.py

import time
import logging
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)
from ai_models import TradingAI, ReinforcementLearning, train_model  # ✅ Added AI model import

# ============================
# 🚀 Order Execution Class
# ============================
class OrderExecution:
    def __init__(self, api_key=None, api_secret=None):
        # Ensure that API key and secret are provided, either explicitly or through configuration
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided.")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(self.api_key, self.api_secret)  # Initialize the Binance client with the API credentials

    def place_market_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0):
        try:
            return self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
        except Exception as e:
            logging.error(f"Market order failed: {e}")
            return {"error": str(e)}

    def place_limit_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0, price=50000.0):
        try:
            return self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=str(price),
                timeInForce=TIME_IN_FORCE_GTC
            )
        except Exception as e:
            logging.error(f"Limit order failed: {e}")
            return {"error": str(e)}

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        try:
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            logging.error(f"Order cancellation failed: {e}")
            return {"error": str(e)}

    def get_open_orders(self, symbol='BTCUSDT'):
        try:
            return self.client.get_open_orders(symbol=symbol)
        except Exception as e:
            logging.error(f"Fetching open orders failed: {e}")
            return {"error": str(e)}

    def execute_trade(self, symbol, side, quantity):
        return self.place_market_order(symbol, side, quantity)

# ============================
# 📈 Optional: Trading Strategy
# ============================
class TradingLogic:
    def __init__(self, api_key=None, api_secret=None, symbol='BTCUSDT', short_window=50, long_window=200):
        # Initialize with given API keys and trading parameters
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position = None
        self.order_executor = OrderExecution(api_key, api_secret)

    def fetch_data(self):
        try:
            data = self.order_executor.client.get_historical_klines(
                self.symbol,
                Client.KLINE_INTERVAL_1HOUR,
                "200 hours ago UTC"
            )
            return {'close': [float(item[4]) for item in data]}
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            return {'close': []}

    def calculate_indicators(self, data):
        closes = data['close']
        if len(closes) < max(self.short_window, self.long_window):
            logging.warning("Not enough data to calculate indicators.")
            return None, None
        short_sma = sum(closes[-self.short_window:]) / self.short_window
        long_sma = sum(closes[-self.long_window:]) / self.long_window
        return short_sma, long_sma

    def check_trade_signal(self, short_sma, long_sma):
        if short_sma > long_sma and self.position != 'long':
            return 'buy'
        elif short_sma < long_sma and self.position != 'short':
            return 'sell'
        return None

    def execute_order(self, signal):
        if signal == 'buy':
            logging.info(f"Executing BUY order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_BUY, 1.0)
            self.position = 'long'
        elif signal == 'sell':
            logging.info(f"Executing SELL order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_SELL, 1.0)
            self.position = 'short'

    def run(self):
        while True:
            try:
                data = self.fetch_data()
                short_sma, long_sma = self.calculate_indicators(data)
                if short_sma is None or long_sma is None:
                    time.sleep(60)
                    continue

                signal = self.check_trade_signal(short_sma, long_sma)
                if signal:
                    self.execute_order(signal)

                time.sleep(60)
            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
                time.sleep(60)

# ============================
# 🧩 App-Compatible Entry
# ============================
def execute_order(symbol, quantity, order_type='market', price=None, side=SIDE_BUY, api_key=None, api_secret=None):
    """
    Standalone function for app.py to place market or limit orders.
    """
    executor = OrderExecution(api_key, api_secret)

    if order_type == 'market':
        return executor.place_market_order(symbol=symbol, side=side, quantity=quantity)
    elif order_type == 'limit':
        if not price:
            return {"error": "Price required for limit order."}
        return executor.place_limit_order(symbol=symbol, side=side, quantity=quantity, price=price)
    else:
        return {"error": f"Unsupported order type: {order_type}"}

# ============================
# 🧪 CLI Testing
# ============================
if __name__ == "__main__":
    # Example API keys for testing (replace with actual values)
    api_key = 'your_api_key_here'
    api_secret = 'your_api_secret_here'
    
    logic = TradingLogic(api_key, api_secret)
    logic.run()
