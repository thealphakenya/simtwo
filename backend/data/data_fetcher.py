# data_fetcher.py
from binance.client import Client
import pandas as pd
import time

class DataFetcher:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def fetch_ohlcv_data(self, symbol='BTCUSDT', interval='1h', limit=100):
        """Fetch OHLCV data (candlestick data) from Binance API."""
        klines = self.client.get_historical_klines(symbol, interval, limit=limit)
        data = []
        for kline in klines:
            # Parse Kline data into a readable format
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
        """Fetch the live order book from Binance."""
        order_book = self.client.get_order_book(symbol=symbol)
        return order_book

    def fetch_ticker(self, symbol='BTCUSDT'):
        """Fetch the latest ticker price from Binance."""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return ticker

    def fetch_balance(self):
        """Fetch account balance."""
        balance = self.client.get_account()
        return balance