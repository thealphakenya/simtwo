from binance.client import Client
import pandas as pd
from datetime import datetime

def fetch_ohlcv_data(api_key, api_secret, symbol="BTCUSDT", interval="1m", limit=100):
    """
    Fetches OHLCV data from Binance for a given symbol and interval.

    Args:
        api_key (str): Binance API Key.
        api_secret (str): Binance API Secret.
        symbol (str): Trading pair (e.g., "BTCUSDT").
        interval (str): Kline interval (e.g., "1m", "5m", "1h").
        limit (int): Number of candles to retrieve.

    Returns:
        pd.DataFrame: DataFrame containing OHLCV data.
    """
    client = Client(api_key, api_secret)
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float
    })

    return df