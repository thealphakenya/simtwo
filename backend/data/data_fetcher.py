# backend/data/data_fetcher.py

from binance.client import Client
import pandas as pd
from backend.config.config import config  # Importing the config object

class DataFetcher:
    def __init__(self, api_key=None, api_secret=None):
        # Use the config values or pass in custom ones
        self.api_key = api_key or config.API_KEY  # Use API_KEY from config
        self.api_secret = api_secret or config.API_SECRET  # Use API_SECRET from config
        self.client = Client(self.api_key, self.api_secret)  # Initialize the Binance client with the API credentials

    def fetch_ohlcv_data(self, symbol=None, interval='1h', limit=100):
        symbol = symbol or config.TRADE_SYMBOL  # Default symbol from config
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
        symbol = symbol or config.TRADE_SYMBOL  # Default symbol from config
        return self.client.get_order_book(symbol=symbol)

    def fetch_ticker(self, symbol=None):
        symbol = symbol or config.TRADE_SYMBOL  # Default symbol from config
        return self.client.get_symbol_ticker(symbol=symbol)

    def fetch_balance(self):
        return self.client.get_account()

# ✅ Convenience wrapper for quick access in app.py
def get_market_data(symbol=None):
    fetcher = DataFetcher()  # Initialize using default API keys from config
    return fetcher.fetch_ticker(symbol)
