# backend/exchange_data.py

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def fetch_ohlcv_data(symbol="BTCUSDT", interval="1m", limit=100):
    # Dummy/mock data generation - replace with real API calls
    end_time = datetime.now()
    timestamps = [end_time - timedelta(minutes=i) for i in range(limit)][::-1]
    prices = np.random.random(size=limit) * 10000 + 20000  # Fake BTC prices

    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Open": prices,
        "High": prices + np.random.rand(limit) * 100,
        "Low": prices - np.random.rand(limit) * 100,
        "Close": prices + np.random.randn(limit) * 10,
        "Volume": np.random.rand(limit) * 10
    })

    return df