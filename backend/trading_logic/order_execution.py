import time
import logging
import numpy as np
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)
from backend.ai_models import TradingAI, ReinforcementLearning  # Corrected import
from backend.victorq.neutralizer import TradingHelper  # This remains the same as you didn't mention changes
from .logic import TradingLogic  # This remains the same as a direct relative import

class OrderExecution:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self.logic = TradingLogic()
        logging.basicConfig(level=logging.INFO)

        # Initialize the ReinforcementLearning model here
        self.reinforcement_model = ReinforcementLearning(api_key, api_secret, time_steps=10, n_features=10)
        
        # Ensure your data (X, y) is prepared somewhere in your code for training
        self.X = None  # Replace with actual feature data
        self.y = None  # Replace with actual target data

    def _validate_order_parameters(self, symbol, quantity, price=None):
        try:
            exchange_info = self.client.get_exchange_info()
            symbol_info = next(item for item in exchange_info['symbols'] if item['symbol'] == symbol)
            min_qty = float(symbol_info['filters'][1]['minQty'])
            qty_step = float(symbol_info['filters'][1]['stepSize'])

            if quantity < min_qty or quantity % qty_step != 0:
                logging.error(f"Invalid quantity for {symbol}: {quantity}")
                return False

            if price:
                min_price = float(symbol_info['filters'][0]['minPrice'])
                max_price = float(symbol_info['filters'][0]['maxPrice'])
                tick_size = float(symbol_info['filters'][0]['tickSize'])

                if price < min_price or price > max_price or price % tick_size != 0:
                    logging.error(f"Invalid price for {symbol}: {price}")
                    return False

            return True
        except Exception as e:
            logging.error(f"Validation error: {e}")
            return False

    def place_market_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0):
        try:
            if not self._validate_order_parameters(symbol, quantity):
                return {"error": "Invalid order parameters."}
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            logging.info(f"Market order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Market order failed: {e}")
            return {"error": str(e)}

    def place_limit_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0, price=50000.0):
        try:
            if not self._validate_order_parameters(symbol, quantity, price):
                return {"error": "Invalid order parameters."}
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=str(price),
                timeInForce=TIME_IN_FORCE_GTC
            )
            logging.info(f"Limit order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Limit order failed: {e}")
            return {"error": str(e)}

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        try:
            cancellation = self.client.cancel_order(symbol=symbol, orderId=order_id)
            logging.info(f"Order cancelled: {cancellation}")
            return cancellation
        except Exception as e:
            logging.error(f"Order cancellation failed: {e}")
            return {"error": str(e)}

    def get_open_orders(self, symbol='BTCUSDT'):
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            logging.info(f"Open orders fetched: {orders}")
            return orders
        except Exception as e:
            logging.error(f"Fetching open orders failed: {e}")
            return {"error": str(e)}

    def execute_trade(self, symbol, side, quantity):
        return self.place_market_order(symbol, side, quantity)

    def calculate_position_size(self, balance):
        return TradingHelper.calculate_position_size(balance)

    # Add this method to trigger model training
    def train_reinforcement_model(self, epochs=50, batch_size=32):
        if self.X is None or self.y is None:
            logging.error("Feature data (X) or target data (y) not provided.")
            return

        # Train the reinforcement learning model using train_model
        self.reinforcement_model.train_model(self.X, self.y, epochs=epochs, batch_size=batch_size)
        logging.info(f"Training complete for {epochs} epochs.")