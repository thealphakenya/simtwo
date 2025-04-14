import time
import logging
import numpy as np
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)
from backend.ai_models import TradingAI, ReinforcementLearning
from backend.victorq.neutralizer import TradingHelper
from .logic import TradingLogic
from backend.ai_models.neural_network import NeuralNetwork

class OrderExecution:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self.logic = TradingLogic()
        logging.basicConfig(level=logging.INFO)

        self.reinforcement_model = ReinforcementLearning(api_key, api_secret, time_steps=10, n_features=10)
        self.nn_model = NeuralNetwork(input_dim=10, output_dim=1)

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

    def train_reinforcement_model(self, epochs=50, batch_size=32):
        if self.X is None or self.y is None:
            logging.error("Feature data (X) or target data (y) not provided.")
            return

        self.reinforcement_model.train_model(self.X, self.y, epochs=epochs, batch_size=batch_size)
        logging.info(f"Training complete for {epochs} epochs.")

    def train_nn_model(self, x_train, y_train, epochs=10, batch_size=32):
        if x_train is None or y_train is None:
            logging.error("Training data not provided.")
            return

        self.nn_model.train(x_train, y_train, epochs=epochs, batch_size=batch_size)
        logging.info(f"Neural Network training complete for {epochs} epochs.")

    def predict_with_nn(self, x_input):
        if x_input is None:
            logging.error("Input data not provided for prediction.")
            return

        try:
            prediction = self.nn_model.predict(x_input)

            if isinstance(prediction, (np.ndarray, list)) and len(prediction) > 0:
                output = float(prediction[0])
            elif isinstance(prediction, (float, int)):
                output = float(prediction)
            else:
                logging.warning(f"Unexpected prediction output: {prediction}")
                return None

            logging.info(f"Prediction: {output}")
            return output

        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            return None