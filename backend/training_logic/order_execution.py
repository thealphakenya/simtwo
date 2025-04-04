import time
import logging
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC

# Order Execution Class
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
            print(f"[Error] Market order failed: {e}")
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
            print(f"[Error] Limit order failed: {e}")
            return None

    def cancel_order(self, symbol='BTCUSDT', order_id=None):
        """Cancels an order."""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return result
        except Exception as e:
            print(f"[Error] Order cancellation failed: {e}")
            return None

    def get_open_orders(self, symbol='BTCUSDT'):
        """Retrieves open orders."""
        try:
            return self.client.get_open_orders(symbol=symbol)
        except Exception as e:
            print(f"[Error] Fetching open orders failed: {e}")
            return []

    def execute_trade(self, symbol, side, quantity):
        """Executes a trade (wrapper for market order)."""
        return self.place_market_order(symbol, side, quantity)


# Trading Logic Class with Binance Integration
class TradingLogic:
    def __init__(self, api_key, api_secret, symbol='BTCUSDT', short_window=50, long_window=200):
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position = None  # No position at the start
        self.order_executor = OrderExecution(api_key, api_secret)

    def fetch_data(self):
        """Fetch market data (this should fetch from Binance or use historical data)."""
        data = self.order_executor.client.get_historical_klines(self.symbol, Client.KLINE_INTERVAL_1HOUR, "200 hours ago UTC")
        return {
            'close': [float(item[4]) for item in data]  # Close prices from the historical data
        }

    def calculate_indicators(self, data):
        """Calculate the short and long moving averages."""
        short_sma = sum(data['close'][-self.short_window:]) / self.short_window  # Simple Moving Average (SMA)
        long_sma = sum(data['close'][-self.long_window:]) / self.long_window
        return short_sma, long_sma

    def check_trade_signal(self, short_sma, long_sma):
        """Check for a trade signal based on the crossover of short and long moving averages."""
        if short_sma > long_sma and self.position != 'long':
            return 'buy'
        elif short_sma < long_sma and self.position != 'short':
            return 'sell'
        else:
            return None  # No trade signal

    def execute_order(self, signal):
        """Executes a trade based on the signal."""
        if signal == 'buy':
            logging.info(f"Executing BUY order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_BUY, 1.0)  # Adjust quantity as needed
            self.position = 'long'
        elif signal == 'sell':
            logging.info(f"Executing SELL order for {self.symbol}")
            self.order_executor.execute_trade(self.symbol, SIDE_SELL, 1.0)  # Adjust quantity as needed
            self.position = 'short'

    def run(self):
        """Main trading loop: fetch data, calculate indicators, check for signals, execute orders."""
        while True:
            try:
                # Step 1: Fetch market data
                data = self.fetch_data()

                # Step 2: Calculate the moving averages
                short_sma, long_sma = self.calculate_indicators(data)

                # Step 3: Check if there’s a trade signal
                signal = self.check_trade_signal(short_sma, long_sma)

                # Step 4: Execute the trade if there’s a signal
                if signal:
                    self.execute_order(signal)

                # Step 5: Sleep for a while before next check (e.g., 60 seconds)
                time.sleep(60)

            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
                time.sleep(60)

# Example API keys for testing
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Instantiate and run the trading logic
trading_logic = TradingLogic(api_key, api_secret)
trading_logic.run()
