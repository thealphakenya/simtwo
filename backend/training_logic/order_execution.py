from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, TIME_IN_FORCE_GTC

class OrderExecution:
    def __init__(self, api_key, api_secret):
        """Initialize the client with provided API key and secret."""
        self.client = Client(api_key, api_secret)

    def place_market_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0):
        """
        Place a market order (buy/sell).
        
        :param symbol: Trading pair symbol (default: BTCUSDT)
        :param side: Side of the trade (buy or sell)
        :param quantity: Quantity of the asset to trade
        :return: Order response if successful, None if error occurs
        """
        try:
            order = self.client.order_market(
                symbol=symbol,
                side=side,
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"Error placing market order: {e}")
            return None

    def place_limit_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0, price=50000.0, time_in_force=TIME_IN_FORCE_GTC):
        """
        Place a limit order (buy/sell).
        
        :param symbol: Trading pair symbol (default: BTCUSDT)
        :param side: Side of the trade (buy or sell)
        :param quantity: Quantity of the asset to trade
        :param price: The price at which the order should be executed
        :param time_in_force: Time in force for the order (default: GTC - Good Till Canceled)
        :return: Order response if successful, None if error occurs
        """
        try:
            order = self.client.order_limit(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=str(price),
                timeInForce=time_in_force
            )
            return order
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        """
        Cancel a specific order.
        
        :param symbol: Trading pair symbol (default: BTCUSDT)
        :param order_id: The order ID to cancel
        :return: Cancellation result if successful, None if error occurs
        """
        try:
            result = self.client.cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            return result
        except Exception as e:
            print(f"Error canceling order: {e}")
            return None

    def get_open_orders(self, symbol='BTCUSDT'):
        """
        Get a list of open orders.
        
        :param symbol: Trading pair symbol (default: BTCUSDT)
        :return: List of open orders if successful, empty list if error occurs
        """
        try:
            open_orders = self.client.get_open_orders(symbol=symbol)
            return open_orders
        except Exception as e:
            print(f"Error getting open orders: {e}")
            return []

