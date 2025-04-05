# backend/data/data_fetcher.py

from binance.client import Client
import pandas as pd

class DataFetcher:
    def __init__(self, api_key=None, api_secret=None, trade_symbol=None):
        # Use the passed API key/secret or fallback to None (it should be passed explicitly if required)
        self.api_key = api_key
        self.api_secret = api_secret
        self.trade_symbol = trade_symbol  # Default trade symbol can be passed here
        
        # Ensure we have API keys before initializing the client
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret must be provided")

        self.client = Client(self.api_key, self.api_secret)  # Initialize the Binance client with the API credentials

    def fetch_ohlcv_data(self, symbol=None, interval='1h', limit=100):
        symbol = symbol or self.trade_symbol  # Use the trade symbol or fallback to instance variable
        klines = self.client.get_historical_klines(symbol, interval, limit=limit)
        data = []
        for kline in klines:
            timestamp = pd.to_datetime(kline[0], unit='ms')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])
        df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        return df

    def fetch_order_book(self, symbol=None):
        symbol = symbol or self.trade_symbol  # Use the trade symbol or fallback to instance variable
        return self.client.get_order_book(symbol=symbol)

    def fetch_ticker(self, symbol=None):
        symbol = symbol or self.trade_symbol  # Use the trade symbol or fallback to instance variable
        return self.client.get_symbol_ticker(symbol=symbol)

    def fetch_balance(self):
        return self.client.get_account()

# ✅ Convenience wrapper for quick access in app.py
def get_market_data(api_key, api_secret, trade_symbol=None):
    fetcher = DataFetcher(api_key=api_key, api_secret=api_secret, trade_symbol=trade_symbol)  # Initialize using provided API keys
    return fetcher.fetch_ticker(trade_symbol)
