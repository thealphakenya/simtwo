# backend/data/data.py
import logging
from binance.client import Client
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class DataFetcher:
    def __init__(self, api_key, api_secret, trade_symbol=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.trade_symbol = trade_symbol
        
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
            logging.info(f"Fetched {len(df)} OHLCV data points.")
            return df
        except Exception as e:
            logging.error(f"Error fetching OHLCV data: {str(e)}")
            raise

    def fetch_order_book(self, symbol=None):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching order book for symbol: {symbol}")
        try:
            order_book = self.client.get_order_book(symbol=symbol)
            return order_book
        except Exception as e:
            logging.error(f"Error fetching order book: {str(e)}")
            raise

    def fetch_ticker(self, symbol=None):
        symbol = symbol or self.trade_symbol
        logging.debug(f"Fetching ticker for symbol: {symbol}")
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return ticker
        except Exception as e:
            logging.error(f"Error fetching ticker: {str(e)}")
            raise

    def fetch_balance(self):
        logging.debug("Fetching account balance")
        try:
            balance = self.client.get_account()
            return balance
        except Exception as e:
            logging.error(f"Error fetching balance: {str(e)}")
            raise

# ✅ Convenience wrapper for quick access
def get_market_data(api_key, api_secret, trade_symbol=None):
    fetcher = DataFetcher(api_key=api_key, api_secret=api_secret, trade_symbol=trade_symbol)
    return fetcher.fetch_ticker(trade_symbol)
