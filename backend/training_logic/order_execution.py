import time
import logging
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC
)

class OrderExecution:
    def __init__(self, api_key, api_secret):
        """Initialize the Binance client with API credentials."""
        self.client = Client(api_key, api_secret)

    def place_market_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0):
        """Places a market order."""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            return order
        except Exception as e:
            logging.error(f"Market order failed: {e}")
            return None

    def place_limit_order(self, symbol='BTCUSDT', side=SIDE_BUY, quantity=1.0, price=50000.0):
        """Places a limit order."""
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
            logging.error(f"Limit order failed: {e}")
            return None

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        """Cancels an order."""
        try:
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            logging.error(f"Order cancellation failed: {e}")
            return None

    def get_open_orders(self, symbol='BTCUSDT'):
        """Retrieves open orders."""
        try:
            return self.client.get_open_orders(symbol=symbol)
        except Exception as e:
            logging.error(f"Fetching open orders failed: {e}")
            return []

    def execute_trade(self, symbol, side, quantity):
        """Executes a trade (wrapper for market order)."""
        return self.place_market_order(symbol, side, quantity)


# Optional: A TradingLogic class for algorithmic logic
class TradingLogic:
    def __init__(self, api_key, api_secret, symbol='BTCUSDT', short_window=50, long_window=200):
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position = None
        self.order_executor = OrderExecution(api_key, api_secret)

    def fetch_data(self):
        """Fetch market data (historical klines)."""
        try:
            data = self.order_executor.client.get_historical_klines(
                self.symbol,
                Client.KLINE_INTERVAL_1HOUR,
                "200 hours ago UTC"
            )
            return {
                'close': [float(item[4]) for item in data]
            }
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            return {'close': []}

    def calculate_indicators(self, data):
        """Calculate SMA indicators."""
        closes = data['close']
        if len(closes) < max(self.short_window, self.long_window):
            logging.warning("Not enough data to calculate indicators.")
            return None, None
        short_sma = sum(closes[-self.short_window:]) / self.short_window
        long_sma = sum(closes[-self.long_window:]) / self.long_window
        return short_sma, long_sma

    def check_trade_signal(self, short_sma, long_sma):
        """Check for crossover signals."""
        if short_sma > long_sma and self.position != 'long':
            return 'buy'
        elif short_sma < long_sma and self.position != 'short':
            return 'sell'
        return None

    def execute_order(self, signal):
        """Execute trade based on signal."""
        if signal == 'buy':
            logging.info(f"Executing BUY order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_BUY, 1.0)
            self.position = 'long'
        elif signal == 'sell':
            logging.info(f"Executing SELL order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_SELL, 1.0)
            self.position = 'short'

    def run(self):
        """Main strategy loop."""
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


# Don't run the bot when this module is imported
if __name__ == "__main__":
    # Only used for manual testing
    api_key = 'your_api_key'
    api_secret = 'your_api_secret'
    trading_logic = TradingLogic(api_key, api_secret)
    trading_logic.run()
