import pandas as pd
from datetime import datetime, timedelta
import random

def fetch_ohlcv_data(symbol="BTCUSDT", interval="1m", limit=100):
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