import time
import logging
import numpy as np
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)
from backend.ai_models.model import TradingAI, ReinforcementLearning, train_model  # Updated AI model import

# ============================
# 🚀 Order Execution Class
# ============================
class OrderExecution:
    def __init__(self, client):
        """
        Instead of API keys, we pass a pre-configured Binance client here.
        """
        self.client = client

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