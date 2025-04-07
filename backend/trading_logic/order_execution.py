import time
import logging
import numpy as np
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
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided.")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(self.api_key, self.api_secret)

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
# 📈 Optional: Trading Strategy with Reinforcement Learning
# ============================
class TradingLogic:
    def __init__(self, api_key=None, api_secret=None, symbol='BTCUSDT', short_window=50, long_window=200):
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position = None
        self.order_executor = OrderExecution(api_key, api_secret)
        self.rl_model = ReinforcementLearning(state_size=3, action_size=3)  # Example state size and action size for RL
        self.previous_state = None
        self.previous_action = None
        self.reward = 0

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

    def get_state(self):
        data = self.fetch_data()
        short_sma, long_sma = self.calculate_indicators(data)
        if short_sma is None or long_sma is None:
            return None
        # Return state as a tuple (short_sma, long_sma, current price)
        current_price = data['close'][-1] if len(data['close']) > 0 else 0
        return np.array([short_sma, long_sma, current_price])

    def execute_order(self, action):
        if action == 0:  # Action 0: Buy
            logging.info(f"Executing BUY order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_BUY, 1.0)
            self.position = 'long'
        elif action == 1:  # Action 1: Sell
            logging.info(f"Executing SELL order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_SELL, 1.0)
            self.position = 'short'
        elif action == 2:  # Action 2: Hold
            logging.info(f"Holding position for {self.symbol}")
            self.position = self.position

    def update_reward(self, action, current_price):
        # Simple reward function: profit/loss from last action
        if self.previous_action is None:
            return 0  # No reward yet

        reward = 0
        if action == 0 and self.previous_action == 1:  # Bought after selling
            reward = current_price - self.previous_price  # Profit from buy action
        elif action == 1 and self.previous_action == 0:  # Sold after buying
            reward = self.previous_price - current_price  # Profit from sell action

        return reward

    def run(self):
        while True:
            try:
                state = self.get_state()
                if state is None:
                    time.sleep(60)
                    continue

                # Get action from the RL model (0: Buy, 1: Sell, 2: Hold)
                action = self.rl_model.act(state)

                # Execute the trade based on the action
                self.execute_order(action)

                # Get current price to calculate reward
                data = self.fetch_data()
                current_price = data['close'][-1] if len(data['close']) > 0 else 0

                # Update reward based on action and previous state
                reward = self.update_reward(action, current_price)
                self.rl_model.remember(self.previous_state, self.previous_action, reward, state)
                self.rl_model.learn()  # Train model with the recent experience

                # Save state and action for next step
                self.previous_state = state
                self.previous_action = action
                self.previous_price = current_price

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
