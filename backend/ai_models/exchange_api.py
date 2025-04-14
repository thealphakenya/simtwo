# backend/exchange_api.py

import logging
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL

logger = logging.getLogger(__name__)

class ExchangeClient:
    def __init__(self, api_key, api_secret):
        if not api_key or not api_secret:
            logger.error("API key or secret missing.")
            raise ValueError("API key and secret must be provided.")
        self.client = Client(api_key, api_secret)
        logger.info("Initialized Binance Client.")

    def place_order(self, symbol, side, quantity, order_type="MARKET"):
        """
        Places a market order on Binance.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT").
            side (str): "BUY" or "SELL".
            quantity (float): Quantity to trade.
            order_type (str): Order type (default is "MARKET").

        Returns:
            dict: Order response from Binance.
        """
        try:
            logger.info(f"Placing {side} order for {quantity} of {symbol}.")
            order = self.client.create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=order_type,
                quantity=quantity
            )
            logger.info("Order placed successfully.")
            return order
        except Exception as e:
            logger.error(f"Order placement failed: {str(e)}")
            raise

    def get_balance(self):
        """
        Retrieves account balance from Binance.

        Returns:
            dict: Account info.
        """
        try:
            logger.debug("Fetching account balance.")
            return self.client.get_account()
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise

    def get_open_orders(self, symbol=None):
        """
        Gets all open orders for the account.

        Args:
            symbol (str, optional): Trading pair symbol. If None, fetches for all symbols.

        Returns:
            list: List of open orders.
        """
        try:
            return self.client.get_open_orders(symbol=symbol) if symbol else self.client.get_open_orders()
        except Exception as e:
            logger.error(f"Failed to fetch open orders: {str(e)}")
            raise