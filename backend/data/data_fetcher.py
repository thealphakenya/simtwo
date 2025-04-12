# backend/data/data_fetcher.py
import logging
from binance.client import Client
import pandas as pd
import numpy as np
from collections import deque
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class DataFetcher:
    def __init__(self, api_key, api_secret, trade_symbol=None, buffer_limit=120):
        self.api_key = api_key
        self.api_secret = api_secret
        self.trade_symbol = trade_symbol
        self.buffer_limit = buffer_limit
        self.ohlcv_buffer = deque(maxlen=self.buffer_limit)

        if not self.api_key or not self.api_secret:
            logging.error("API Key or Secret is missing!")
            raise ValueError("API key and secret must be provided")

        logging.info("Initializing Binance Client with provided API keys.")
        self.client = Client(self.api_key, self.api_secret)

    def fetch_ohlcv_data(self, symbol=None, interval='1h', limit=100):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching OHLCV data for symbol: {symbol} with interval: {interval}")
        
        try:
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

            # Update buffer
            for _, row in df.iterrows():
                self.ohlcv_buffer.append(row.to_dict())

            logging.info(f"Fetched {len(df)} OHLCV data points.")
            return df
        except Exception as e:
            logging.error(f"Error fetching OHLCV data: {str(e)}")
            raise

    def get_latest_feature_frame(self):
        """
        Returns a processed feature frame for model prediction.
        """
        if len(self.ohlcv_buffer) < 20:
            logging.warning("Not enough data in buffer for feature frame.")
            return None

        df = pd.DataFrame(list(self.ohlcv_buffer)).copy()
        df.set_index('Timestamp', inplace=True)

        # Feature Engineering
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['RSI_14'] = self.calculate_rsi(df['Close'], period=14)
        df['MACD'], df['MACD_signal'] = self.calculate_macd(df['Close'])

        df.dropna(inplace=True)
        latest = df.iloc[-1]
        features = latest[['Close', 'EMA_10', 'RSI_14', 'MACD', 'MACD_signal']]

        logging.debug(f"Feature vector for model: {features.to_dict()}")
        return features.values.reshape(1, -1)

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, series, fast=12, slow=26, signal=9):
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    def fetch_order_book(self, symbol=None):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching order book for symbol: {symbol}")
        try:
            return self.client.get_order_book(symbol=symbol)
        except Exception as e:
            logging.error(f"Error fetching order book: {str(e)}")
            raise

    def fetch_ticker(self, symbol=None):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching ticker for symbol: {symbol}")
        try:
            return self.client.get_symbol_ticker(symbol=symbol)
        except Exception as e:
            logging.error(f"Error fetching ticker: {str(e)}")
            raise

    def fetch_balance(self):
        logging.debug("Fetching account balance")
        try:
            return self.client.get_account()
        except Exception as e:
            logging.error(f"Error fetching balance: {str(e)}")
            raise

    def fetch_chart_data(self, symbol=None, interval='1m', limit=20):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching chart data for symbol: {symbol}, interval: {interval}, limit: {limit}")
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            return [
                {
                    "timestamp": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                }
                for k in klines
            ]
        except Exception as e:
            logging.error(f"Error fetching chart data: {str(e)}")
            return []

# ✅ Convenience wrapper for quick access
def get_market_data(api_key, api_secret, trade_symbol=None):
    fetcher = DataFetcher(api_key=api_key, api_secret=api_secret, trade_symbol=trade_symbol)
    return fetcher.fetch_ticker(trade_symbol)