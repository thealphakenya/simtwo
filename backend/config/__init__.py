import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("BINANCE_API_KEY")
    API_SECRET = os.getenv("BINANCE_SECRET_KEY")
    TRADE_SYMBOL = 'BTCUSDT'
    TRADE_QUANTITY = 0.01
    WEBHOOK_SECRET = 'your_secret_here'
