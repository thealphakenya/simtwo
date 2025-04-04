from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC

class OrderExecution:
    def __init__(self, api_key, api_secret):
        """Initialize the Binance client with API credentials."""
        self.client = Client(api_key, api_secret)

    def place_market_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0):
        """
        Places a market order.

        :param symbol: Trading pair symbol (e.g., BTCUSDT)
        :param side: Trade direction ('BUY' or 'SELL')
        :param quantity: Amount of asset to trade
        :return: Order response or None if an error occurs
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"[Error] Market order failed: {e}")
            return None

    def place_limit_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0, price=50000.0):
        """
        Places a limit order.

        :param symbol: Trading pair symbol (e.g., BTCUSDT)
        :param side: Trade direction ('BUY' or 'SELL')
        :param quantity: Amount of asset to trade
        :param price: Order execution price
        :return: Order response or None if an error occurs
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=str(price),
                timeInForce=TIME_IN_FORCE_GTC
            )
            return order
        except Exception as e:
            print(f"[Error] Limit order failed: {e}")
            return None

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        """
        Cancels an order.

        :param symbol: Trading pair symbol
        :param order_id: Order ID to cancel
        :return: Cancellation response or None if an error occurs
        """
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return result
        except Exception as e:
            print(f"[Error] Order cancellation failed: {e}")
            return None

    def get_open_orders(self, symbol='BTCUSDT'):
        """
        Retrieves open orders.

        :param symbol: Trading pair symbol
        :return: List of open orders or an empty list if an error occurs
        """
        try:
            return self.client.get_open_orders(symbol=symbol)
        except Exception as e:
            print(f"[Error] Fetching open orders failed: {e}")
            return []

    def execute_trade(self, symbol, side, quantity):
        """
        Executes a trade (wrapper for market order).

        :param symbol: Trading pair symbol
        :param side: Trade direction ('BUY' or 'SELL')
        :param quantity: Amount of asset to trade
        :return: Order response or None if an error occurs
        """
        return self.place_market_order(symbol, side, quantity)


# Standalone function for executing a trade (Optional)
def execute_trade():
    print("Executing trade using OrderExecution class.")
