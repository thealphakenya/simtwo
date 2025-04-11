import time
import logging
import numpy as np
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)
from backend.ai_models.model import TradingAI, ReinforcementLearning, train_model
from backend.victorq.neutralizer import TradingHelper  # Shared logic

class OrderExecution:
    def __init__(self, client):
        self.client = client
        logging.basicConfig(level=logging.INFO)

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