# backend/data/data_fetcher.py

from binance.client import Client
import pandas as pd
from config import config

class DataFetcher:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def fetch_ohlcv_data(self, symbol='BTCUSDT', interval='1h', limit=100):
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

    def fetch_order_book(self, symbol='BTCUSDT'):
        return self.client.get_order_book(symbol=symbol)

    def fetch_ticker(self, symbol='BTCUSDT'):
        return self.client.get_symbol_ticker(symbol=symbol)

    def fetch_balance(self):
        return self.client.get_account()

# ✅ Convenience wrapper for quick access in app.py
def get_market_data(symbol='BTCUSDT'):
    fetcher = DataFetcher(config.API_KEY, config.API_SECRET)
    return fetcher.fetch_ticker(symbol)
