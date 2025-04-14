import pandas as pd
from datetime import datetime, timedelta
import random

def fetch_ohlcv_data(symbol="BTCUSDT", interval="1m", limit=100):
    now = datetime.utcnow()
    dates = [now - timedelta(minutes=i) for i in range(limit)][::-1]

    data = {
        "timestamp": dates,
        "open": [random.uniform(20000, 30000) for _ in range(limit)],
        "high": [random.uniform(20000, 30000) for _ in range(limit)],
        "low": [random.uniform(20000, 30000) for _ in range(limit)],
        "close": [random.uniform(20000, 30000) for _ in range(limit)],
        "volume": [random.uniform(1, 100) for _ in range(limit)],
    }

    df = pd.DataFrame(data)
    return df