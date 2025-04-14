# backend/exchange/exchange_data.py

import logging
import pandas as pd
from backend.exchange_api import ExchangeClient  # Import your exchange client to interact with the exchange
from datetime import datetime, timedelta
import random

# Set up logger
logger = logging.getLogger(__name__)

def fetch_ohlcv_data(symbol, interval='1h', limit=100, use_external=False):
    """
    Fetches OHLCV data from Binance or an external simulated source based on the use_external flag.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
        interval (str): Time interval for data points (default is '1h').
        limit (int): Number of data points to fetch (default is 100).
        use_external (bool): Whether to fetch data from the external source.

    Returns:
        pd.DataFrame: OHLCV data
    """
    if use_external:
        logger.info("Fetching OHLCV data from external source for symbol %s", symbol)
        # Fetch simulated or external data here
        return fetch_external_ohlcv_data(symbol, interval, limit)
    else:
        logger.info("Fetching OHLCV data from Binance for symbol %s", symbol)
        # Fetch data from Binance or other exchange
        return fetch_binance_ohlcv_data(symbol, interval, limit)


def fetch_external_ohlcv_data(symbol, interval, limit):
    """
    Simulates OHLCV data for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., "BTCUSDT").
        interval (str): The interval between each data point (e.g., "1m", "5m").
        limit (int): Number of data points to return.

    Returns:
        pd.DataFrame: DataFrame containing simulated OHLCV data.
    """
    now = datetime.utcnow()
    dates = [now - timedelta(minutes=i) for i in range(limit)][::-1]

    base_prices = [random.uniform(20000, 30000) for _ in range(limit)]

    data = {
        "timestamp": dates,
        "open": base_prices,
        "high": [p + random.uniform(0, 500) for p in base_prices],
        "low": [p - random.uniform(0, 500) for p in base_prices],
        "close": [p + random.uniform(-250, 250) for p in base_prices],
        "volume": [random.uniform(1, 100) for _ in range(limit)],
    }

    df = pd.DataFrame(data)
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def fetch_binance_ohlcv_data(symbol, interval, limit):
    """
    Fetches OHLCV data from Binance using the provided symbol, interval, and limit.

    Args:
        symbol (str): The trading pair symbol (e.g., "BTCUSDT").
        interval (str): The interval between each data point (e.g., "1m", "5m").
        limit (int): Number of data points to fetch.

    Returns:
        pd.DataFrame: DataFrame containing OHLCV data from Binance.
    """
    client = ExchangeClient(api_key="your_api_key", api_secret="your_api_secret")  # Initialize the client
    klines = client.get_historical_klines(symbol, interval, limit=limit)

    data = [
        [
            pd.to_datetime(k[0], unit='ms'),
            float(k[1]),
            float(k[2]),
            float(k[3]),
            float(k[4]),
            float(k[5])
        ]
        for k in klines
    ]
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df